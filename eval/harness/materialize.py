"""Build a trial working directory for a variant.

Responsibilities:
  - Create a fresh trial dir under a configurable work-dir (default /tmp).
  - Drop the task's initial_files into it.
  - For with-refs variants: hard-link the reference pool, copy the rule,
    render the hook settings, and set permissions.
  - For without-refs variants: just the task files; no .claude, no refs.

Trials MUST run outside dev_template/ so no parent CLAUDE.md leaks in.
Hard links used for the reference tree — not symlinks (per user constraint)
and not copies (26MB per trial would be wasteful across ~100s of trials).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path

# Repo root — used to locate the reference pool and template files.
REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = REPO_ROOT / "reference" / "stan"
TEMPLATE_CLAUDE_DIR = REPO_ROOT / "template" / "modules" / "_always" / "files" / ".claude"
TRIAL_HOOKS_DIR = REPO_ROOT / "eval" / "harness" / "trial_hooks"
STOP_VALIDATION_HOOK = REPO_ROOT / ".claude" / "hooks" / "stop-validation.py"

VARIANTS = ("with_refs", "without_refs")
ITERATION_MODES = ("single_shot", "iterative")

ITERATION_PROMPT_SUFFIX = """

ITERATION BUDGET: You have up to 10 attempts. After writing model.stan, validate it by compiling and fitting on the provided data (data.json in the current directory). Use cmdstanpy or CmdStan. If the fit has divergences > 0, R-hat > 1.05, or errors, diagnose and fix the issue, then rewrite/re-fit. Only finalize your output when the model compiles and fits cleanly on the data, or when you have exhausted the 10-attempt budget. Report what you tried and why in a summary."""


def materialize(
    variant: str,
    initial_files: dict[str, str],
    work_dir: Path | str = "/tmp",
    run_id: str | None = None,
    iteration_mode: str = "single_shot",
) -> Path:
    """Create a trial directory for the given variant + iteration mode.

    Returns the absolute path to the created trial directory.

    Args:
        variant: one of 'with_refs', 'without_refs'.
        initial_files: {relative_path: content} files to create in the trial dir.
        work_dir: parent directory under which the trial dir is created.
        run_id: optional grouping for trials belonging to the same run.
        iteration_mode: 'single_shot' (no Stop hook) or 'iterative' (Stop hook
            forces Claude to execute code between edits). Applies to both
            ref variants; with_refs may additionally install the search hook.
    """
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}, got {variant!r}")
    if iteration_mode not in ITERATION_MODES:
        raise ValueError(f"iteration_mode must be one of {ITERATION_MODES}, got {iteration_mode!r}")

    work_dir = Path(work_dir)
    group = f"eval-{run_id}" if run_id else "eval"
    trial_dir = work_dir / group / f"trial-{uuid.uuid4().hex[:12]}"
    trial_dir.mkdir(parents=True, exist_ok=False)

    _write_initial_files(trial_dir, initial_files)

    if variant == "with_refs":
        _install_reference_pool(trial_dir)

    if variant == "with_refs" or iteration_mode == "iterative":
        _install_claude_config(trial_dir, with_refs=(variant == "with_refs"), iterative=(iteration_mode == "iterative"))

    return trial_dir


def _write_initial_files(trial_dir: Path, files: dict[str, str]) -> None:
    for rel_path, content in files.items():
        target = trial_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def _install_reference_pool(trial_dir: Path) -> None:
    """Hard-link the reference/stan tree into the trial dir.

    Uses `cp -al` (archive + hard-link) which preserves directory structure,
    creates hard links for regular files, and doesn't consume extra disk.
    Hard-linked files are indistinguishable from copies for the running process.
    """
    if not REFERENCE_DIR.exists():
        raise FileNotFoundError(f"reference pool not found at {REFERENCE_DIR}")

    dest = trial_dir / "reference" / "stan"
    dest.parent.mkdir(parents=True, exist_ok=True)

    # `cp -al SRC DST` requires DST not to exist (or acts oddly); create parent only.
    subprocess.run(
        ["cp", "-al", str(REFERENCE_DIR), str(dest)],
        check=True,
        capture_output=True,
    )


def _install_claude_config(trial_dir: Path, *, with_refs: bool, iterative: bool) -> None:
    """Install .claude/ config. What gets installed depends on the two dimensions:

    with_refs=True:
      - rules/stan.md (advisory rule)
      - hooks/inject-stan-refs.sh + UserPromptSubmit registration (pre-inject refs)
      - permissions allow the search script
    iterative=True:
      - hooks/stop-validation.py + Stop registration (force validation)

    Both can be True simultaneously (pilot 2's with_refs+iterative setup).
    """
    claude_dir = trial_dir / ".claude"
    (claude_dir / "hooks").mkdir(parents=True, exist_ok=True)

    hooks_config: dict[str, list] = {}
    permissions_allow = ["Read", "Glob", "Grep", "Bash(python3 *)"]

    if with_refs:
        (claude_dir / "rules").mkdir(parents=True, exist_ok=True)
        shutil.copy2(TEMPLATE_CLAUDE_DIR / "rules" / "stan.md", claude_dir / "rules" / "stan.md")

        inject_dst = claude_dir / "hooks" / "inject-stan-refs.sh"
        shutil.copy2(TRIAL_HOOKS_DIR / "inject-stan-refs.sh", inject_dst)
        inject_dst.chmod(0o755)

        permissions_allow.append("Bash(bash reference/stan/search.sh *)")
        hooks_config["UserPromptSubmit"] = [{
            "matcher": "",
            "hooks": [{
                "type": "command",
                "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/inject-stan-refs.sh",
            }],
        }]

    if iterative:
        stop_dst = claude_dir / "hooks" / "stop-validation.py"
        shutil.copy2(STOP_VALIDATION_HOOK, stop_dst)
        stop_dst.chmod(0o755)

        hooks_config["Stop"] = [{
            "matcher": "",
            "hooks": [{
                "type": "command",
                "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/stop-validation.py",
            }],
        }]

    settings: dict = {"permissions": {"allow": permissions_allow}}
    if hooks_config:
        settings["hooks"] = hooks_config
    (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2))


def cleanup(trial_dir: Path) -> None:
    """Remove a trial directory. Safe no-op if it doesn't exist."""
    if trial_dir.exists():
        shutil.rmtree(trial_dir)

"""Run a single trial end-to-end: materialize, invoke Claude, score, record.

The `claude_bin` parameter is configurable so tests can swap in a mock binary
instead of hitting the real Claude Code subscription.
"""
from __future__ import annotations

import os
import platform
import resource
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from eval.harness.materialize import ITERATION_PROMPT_SUFFIX, cleanup, materialize
from eval.harness.spec import TaskSpec, TrialResult

SCORER_TIMEOUT_S = 900  # 15 min max per scorer call (compile + fit + judge)


def _score_with_timeout(scorer, trial_dir: Path, timeout_s: int) -> dict:
    """Run scorer in a thread with a timeout. If it hangs, kill cmdstan children."""
    holder: dict = {"result": None, "error": None}

    def worker():
        try:
            holder["result"] = scorer(trial_dir)
        except Exception as e:  # noqa: BLE001
            holder["error"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout=timeout_s)

    if t.is_alive():
        # Scorer hung (most likely cmdstan stuck). Kill cmdstan subprocess tree.
        try:
            import psutil
            for child in psutil.Process(os.getpid()).children(recursive=True):
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
        except ImportError:
            pass
        # Give the thread a moment to unblock and record its error (if any)
        t.join(timeout=10)
        return {"scorer_timeout": True, "timeout_s": timeout_s}

    if holder["error"] is not None:
        return {"scorer_error": holder["error"]}
    return holder["result"] or {}


def run_trial(
    spec: TaskSpec,
    model: str,
    variant: str,
    trial_n: int,
    run_id: str,
    seed: int,
    work_dir: Path | str = "/tmp",
    claude_bin: str = "claude",
    keep_dir: bool = False,
    git_sha: str = "unknown",
    claude_code_version: str = "unknown",
    iteration_mode: str = "single_shot",
) -> TrialResult:
    """Run one trial and return the result.

    Side effects:
      - Creates and populates a trial directory under work_dir.
      - Writes stdout/stderr files next to the trial dir (preserved even on cleanup).
      - Calls spec.scorer(trial_dir) if provided.

    Returns a TrialResult (not yet written to JSONL; the caller does that).
    """
    trial_id = uuid.uuid4().hex[:12]

    # Separate directory for captured output — lives alongside the trial dir's parent
    # so stdout/stderr survive even when the trial dir is cleaned up.
    output_dir = Path(work_dir) / f"eval-{run_id}" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / f"trial-{trial_id}.stdout"
    stderr_path = output_dir / f"trial-{trial_id}.stderr"

    trial_dir = materialize(
        variant=variant,
        initial_files=spec.initial_files,
        work_dir=work_dir,
        run_id=run_id,
        iteration_mode=iteration_mode,
    )

    prompt = spec.prompt + (ITERATION_PROMPT_SUFFIX if iteration_mode == "iterative" else "")

    t0 = time.monotonic()
    exit_code: int | None = None
    status = "completed"

    try:
        # --dangerously-skip-permissions: headless mode can't prompt, so any tool
        # that would normally ask the user (Write, Bash) would silently fail. The
        # trial dir is under /tmp, isolated from the user's files, so bypass is safe.
        proc = subprocess.run(
            [claude_bin, "-p", prompt, "--model", model, "--dangerously-skip-permissions"],
            cwd=str(trial_dir),
            capture_output=True,
            text=True,
            timeout=spec.timeout_s,
            check=False,
        )
        exit_code = proc.returncode
        stdout_path.write_text(proc.stdout)
        stderr_path.write_text(proc.stderr)
    except subprocess.TimeoutExpired as e:
        status = "timeout"
        stdout_path.write_text(e.stdout or "")
        stderr_path.write_text((e.stderr or "") + f"\n\n[TIMEOUT after {spec.timeout_s}s]")
    except FileNotFoundError as e:
        status = "crashed"
        stdout_path.write_text("")
        stderr_path.write_text(f"[FileNotFoundError] {e}")
    except Exception as e:  # noqa: BLE001 — harness boundary; record and continue
        status = "crashed"
        stdout_path.write_text("")
        stderr_path.write_text(f"[{type(e).__name__}] {e}")

    wall_clock = time.monotonic() - t0

    # Score the trial (only if subprocess actually ran and a scorer is provided).
    # Wrapped in a timeout so a pathological model can't hang the whole run.
    metrics: dict = {}
    if status == "completed" and spec.scorer is not None:
        metrics = _score_with_timeout(spec.scorer, trial_dir, SCORER_TIMEOUT_S)

    result = TrialResult(
        run_id=run_id,
        trial_id=trial_id,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        git_sha=git_sha,
        task_id=spec.id,
        model=model,
        variant=variant,
        iteration_mode=iteration_mode,
        trial_n=trial_n,
        seed=seed,
        wall_clock_s=round(wall_clock, 3),
        subprocess_exit=exit_code,
        status=status,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        metrics=metrics,
        python_version=platform.python_version(),
        claude_code_version=claude_code_version,
    )

    if not keep_dir:
        cleanup(trial_dir)

    return result

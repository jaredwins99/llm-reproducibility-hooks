"""CLI entrypoint for the eval harness.

Runs a configured grid of (task × model × variant × trial) cells. For each
cell, materializes a trial directory, invokes Claude, scores, and appends a
JSONL result line.

Usage:
    python -m eval.harness.run \\
        --tasks smoke.hello \\
        --models claude-opus-4-7 \\
        --variants without_refs with_refs \\
        --trials-per-cell 3 \\
        --claude-bin /tmp/fake-claude.sh
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from eval.harness.runner import run_trial
from eval.tasks import REGISTRY, get_task

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "eval" / "results"


def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _claude_code_version(claude_bin: str) -> str:
    try:
        out = subprocess.run(
            [claude_bin, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return (out.stdout or out.stderr).strip().splitlines()[0][:80]
    except Exception:
        return "unknown"


def _auto_import_tasks() -> None:
    """Import all modules in eval/tasks/ so they self-register.

    Walks the tasks directory and imports each .py file (except __init__).
    Keeps registration explicit — nothing auto-magical beyond the import.
    """
    import importlib

    tasks_dir = REPO_ROOT / "eval" / "tasks"
    for path in tasks_dir.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        rel = path.relative_to(REPO_ROOT).with_suffix("")
        module_name = ".".join(rel.parts)
        importlib.import_module(module_name)


def main(argv: list[str] | None = None) -> int:
    _auto_import_tasks()

    parser = argparse.ArgumentParser(description="Eval harness runner")
    parser.add_argument("--tasks", nargs="+", required=True,
                        help=f"task ids; known: {sorted(REGISTRY)}")
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--variants", nargs="+", default=["with_refs", "without_refs"])
    parser.add_argument("--iteration-modes", nargs="+", default=["single_shot"],
                        choices=["single_shot", "iterative"],
                        help="One or more iteration modes. 'iterative' installs the Stop hook and adds an iteration instruction to the prompt.")
    parser.add_argument("--trials-per-cell", type=int, default=3)
    parser.add_argument("--work-dir", default="/tmp")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--keep-dirs", action="store_true",
                        help="preserve trial directories after each run (debugging)")
    parser.add_argument("--run-id", default=None,
                        help="override auto-generated run id (YYYYMMDD-HHMMSS)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / f"{run_id}.jsonl"

    git_sha = _git_sha()
    claude_version = _claude_code_version(args.claude_bin)

    specs = [get_task(tid) for tid in args.tasks]
    total_cells = (
        len(specs) * len(args.models) * len(args.variants)
        * len(args.iteration_modes) * args.trials_per_cell
    )

    print(f"run_id={run_id} cells={total_cells} results={results_path}", file=sys.stderr)

    cell_n = 0
    with open(results_path, "a", buffering=1) as f:
        for spec in specs:
            for model in args.models:
                for variant in args.variants:
                    for iteration_mode in args.iteration_modes:
                        for trial_n in range(args.trials_per_cell):
                            cell_n += 1
                            print(f"[{cell_n}/{total_cells}] {spec.id} {model} {variant} "
                                  f"iter={iteration_mode} trial={trial_n}", file=sys.stderr)
                            result = run_trial(
                                spec=spec,
                                model=model,
                                variant=variant,
                                trial_n=trial_n,
                                run_id=run_id,
                                seed=args.seed,
                                work_dir=args.work_dir,
                                claude_bin=args.claude_bin,
                                keep_dir=args.keep_dirs,
                                git_sha=git_sha,
                                claude_code_version=claude_version,
                                iteration_mode=iteration_mode,
                            )
                            f.write(json.dumps(result.to_json()) + "\n")
                            print(f"    status={result.status} wall={result.wall_clock_s}s "
                                  f"metrics={result.metrics}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

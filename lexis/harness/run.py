"""CLI entrypoint for the lexis pipeline.

Runs N trials of the 5-agent chain, each with the configured arms, appending
one JSONL row per (trial, arm) to lexis/results/<run_id>.jsonl.

Usage:
    python -m lexis.harness.run --trials 10 --run-id pilot1
    python -m lexis.harness.run --trials 2 --claude-bin /tmp/fake-lexis-claude.sh --run-id smoke
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from lexis.harness.pipeline import run_trial

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "lexis" / "results"

# Rotating diversity hints so stage A doesn't converge on the same few topics.
SEED_HINTS = [
    "food and diet", "land use and wildlife", "technology in daily life",
    "work and labor", "education and child-rearing", "medicine and the body",
    "money and trade", "transport and cities", "art and entertainment",
    "law and punishment", "sport and competition", "religion and ritual",
    "science funding", "privacy and surveillance", "energy and climate",
]


def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lexis pipeline runner")
    parser.add_argument("--trials", type=int, required=True)
    parser.add_argument("--arms", nargs="+", default=["lexis", "control"])
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--work-dir", default="/home/godli/eval-work")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--model-a", default="opus")
    parser.add_argument("--model-b", default="opus")
    parser.add_argument("--model-c", default="opus")
    parser.add_argument("--model-d", default="opus")
    parser.add_argument("--model-e", default="opus")
    args = parser.parse_args(argv)

    run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / f"{run_id}.jsonl"
    git_sha = _git_sha()
    stage_models = {"A": args.model_a, "B": args.model_b, "C": args.model_c,
                    "D": args.model_d, "E": args.model_e}

    print(f"run_id={run_id} trials={args.trials} arms={args.arms} results={results_path}",
          file=sys.stderr)

    with open(results_path, "a", buffering=1) as f:
        for n in range(args.trials):
            seed_hint = SEED_HINTS[n % len(SEED_HINTS)]
            print(f"[{n + 1}/{args.trials}] seed_hint={seed_hint!r}", file=sys.stderr)
            rows = run_trial(
                trial_n=n, run_id=run_id, seed_hint=seed_hint,
                arms=tuple(args.arms), claude_bin=args.claude_bin,
                work_dir=args.work_dir, stage_models=stage_models, git_sha=git_sha,
            )
            for row in rows:
                f.write(json.dumps(row) + "\n")
            summary = {r["arm"]: r["answer"] for r in rows}
            status = rows[0]["status"] if rows else "?"
            print(f"    status={status} topic={rows[0].get('topic')!r} "
                  f"role={rows[0].get('role')!r} answers={summary}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

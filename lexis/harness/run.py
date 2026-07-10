"""CLI entrypoint for the lexis pipeline.

Runs trials of the 5-agent chain, each with the configured arms, appending
one JSONL row per (trial, arm) to lexis/results/<run_id>.jsonl.

Topics come from the human-vetted bank by default (lexis/topics/approved.jsonl,
built via gen_topics.py + manual review). Pass --live-topics to let stage A
generate topics on the fly instead (unvetted).

Usage:
    python -m lexis.harness.run --trials 10 --run-id pilot1
    python -m lexis.harness.run --trials 2 --live-topics \\
        --claude-bin /tmp/fake-lexis-claude.sh --run-id smoke
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from lexis.harness.pipeline import DEFAULT_ARMS, run_trial

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "lexis" / "results"
APPROVED_TOPICS = REPO_ROOT / "lexis" / "topics" / "approved.jsonl"
APPROVED_ROLES = REPO_ROOT / "lexis" / "roles" / "approved.jsonl"

# Rotating diversity hints. SEED_HINTS steer stage A when --live-topics is on;
# ROLE_HINTS steer stage B (always live, independent of topic).
SEED_HINTS = [
    "food and diet", "land use and wildlife", "technology in daily life",
    "work and labor", "education and child-rearing", "medicine and the body",
    "money and trade", "transport and cities", "art and entertainment",
    "law and punishment", "sport and competition", "religion and ritual",
    "science funding", "privacy and surveillance", "energy and climate",
]
ROLE_HINTS = [
    "outdoor and land-based trades", "maritime occupations", "medical professions",
    "military and veterans", "religious communities", "artistic scenes",
    "skilled manual trades", "rural agricultural communities", "finance and trading floors",
    "aviation", "long-haul transport", "competitive sport subcultures",
    "academic disciplines", "gaming and online communities", "law enforcement",
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


def _load_bank(path: Path, kind: str, gen_hint: str) -> list[dict]:
    if not path.exists():
        print(f"ERROR: vetted {kind} bank not found at {path}.\n{gen_hint}", file=sys.stderr)
        sys.exit(1)
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    if not rows:
        print(f"ERROR: {kind} bank at {path} is empty.", file=sys.stderr)
        sys.exit(1)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lexis pipeline runner")
    parser.add_argument("--trials", type=int, default=None,
                        help="cap on trial count (default: full topic x role factorial)")
    parser.add_argument("--arms", nargs="+", default=list(DEFAULT_ARMS))
    parser.add_argument("--live-topics", action="store_true",
                        help="let stage A generate topics live instead of using the vetted bank")
    parser.add_argument("--live-roles", action="store_true",
                        help="let stage B pick roles live instead of using the vetted bank")
    parser.add_argument("--topics", default=str(APPROVED_TOPICS),
                        help="path to the vetted topic bank (jsonl)")
    parser.add_argument("--roles", default=str(APPROVED_ROLES),
                        help="path to the vetted role bank (jsonl)")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--work-dir", default="/home/godli/eval-work")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--model-a", default="sonnet")
    parser.add_argument("--model-b", default="sonnet")
    parser.add_argument("--model-c", default="sonnet")
    parser.add_argument("--model-d", default="sonnet")
    parser.add_argument("--model-e", default="opus")
    args = parser.parse_args(argv)

    topic_bank = None if args.live_topics else _load_bank(
        Path(args.topics), "topic",
        "Generate candidates with `python -m lexis.harness.gen_topics --n 30`, review, "
        "copy approved lines there. Or pass --live-topics.")
    role_bank = None if args.live_roles else _load_bank(
        Path(args.roles), "role",
        "See lexis/ROLES.md; approved roles go in that file. Or pass --live-roles.")

    # Trial plan: full factorial over available banks; live stages get rotating hints.
    if topic_bank and role_bank:
        plan = [(t, r) for t in topic_bank for r in role_bank]
    elif topic_bank:
        plan = [(t, None) for t in topic_bank]
    elif role_bank:
        plan = [(None, r) for r in role_bank]
    else:
        plan = [(None, None)] * (args.trials or 10)
    if args.trials is not None:
        plan = plan[: args.trials]

    run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / f"{run_id}.jsonl"
    git_sha = _git_sha()
    stage_models = {"A": args.model_a, "B": args.model_b, "C": args.model_c,
                    "D": args.model_d, "E": args.model_e}

    print(f"run_id={run_id} trials={len(plan)} arms={args.arms} "
          f"topics={'live' if topic_bank is None else f'bank({len(topic_bank)})'} "
          f"roles={'live' if role_bank is None else f'bank({len(role_bank)})'} "
          f"results={results_path}", file=sys.stderr)

    with open(results_path, "a", buffering=1) as f:
        for n, (preset_topic, preset_role) in enumerate(plan):
            seed_hint = SEED_HINTS[n % len(SEED_HINTS)]
            role_hint = ROLE_HINTS[n % len(ROLE_HINTS)]
            t_label = preset_topic["topic"] if preset_topic else f"live:{seed_hint}"
            r_label = preset_role["role"] if preset_role else f"live:{role_hint}"
            print(f"[{n + 1}/{len(plan)}] topic={t_label!r} role={r_label!r}", file=sys.stderr)
            rows = run_trial(
                trial_n=n, run_id=run_id, seed_hint=seed_hint, role_hint=role_hint,
                arms=tuple(args.arms), claude_bin=args.claude_bin,
                work_dir=args.work_dir, stage_models=stage_models, git_sha=git_sha,
                preset_topic=preset_topic, preset_role=preset_role,
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

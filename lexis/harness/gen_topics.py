"""Generate candidate topics for human vetting.

Runs stage A only, N times with rotating diversity hints, writing candidates
to lexis/topics/candidates.jsonl. Review them, then copy the approved ones
into lexis/topics/approved.jsonl (same schema, one JSON object per line) —
run.py --topics consumes that file.

Usage:
    python -m lexis.harness.gen_topics --n 30
    python -m lexis.harness.gen_topics --n 5 --claude-bin /tmp/fake-lexis-claude.sh
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from lexis.harness.pipeline import DEFAULT_STAGE_MODELS, _fill, _load_template, run_stage

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPICS_DIR = REPO_ROOT / "lexis" / "topics"

SEED_HINTS = [
    "food and diet", "land use and wildlife", "technology in daily life",
    "work and labor", "education and child-rearing", "medicine and the body",
    "money and trade", "transport and cities", "art and entertainment",
    "law and punishment", "sport and competition", "religion and ritual",
    "science funding", "privacy and surveillance", "energy and climate",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate topic candidates for vetting")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--model", default=DEFAULT_STAGE_MODELS["A"])
    parser.add_argument("--out", default=str(TOPICS_DIR / "candidates.jsonl"))
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    required = {"topic", "demand", "answer_instruction", "allowed_answers"}

    with open(out_path, "a", buffering=1) as f, tempfile.TemporaryDirectory() as tmp:
        for n in range(args.n):
            seed_hint = SEED_HINTS[n % len(SEED_HINTS)]
            print(f"[{n + 1}/{args.n}] seed_hint={seed_hint!r}", file=sys.stderr)
            a = run_stage("A", _fill(_load_template("stage_a_topic.md"), seed_hint=seed_hint),
                          args.model, args.claude_bin, Path(tmp))
            if a.parsed is None or not required <= set(a.parsed):
                print(f"    unparseable — skipped (status={a.status})", file=sys.stderr)
                continue
            record = {**a.parsed, "seed_hint": seed_hint}
            f.write(json.dumps(record) + "\n")
            print(f"    topic={a.parsed['topic']!r}", file=sys.stderr)

    print(f"\nCandidates appended to {out_path}", file=sys.stderr)
    print("Review, then copy approved lines to lexis/topics/approved.jsonl", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

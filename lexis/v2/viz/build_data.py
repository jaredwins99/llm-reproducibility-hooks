"""Build data.json for the lexis viz page from pilot result JSONL + trial dirs.

Reads:
  lexis/results/pilot1.jsonl        (v1, drifty translations)
  lexis/v2/results/pilot2.jsonl     (v2, pinned truth conditions + drift gate)
  /home/godli/eval-work/lexis-pilot2/trial-*/bundle.json  (exact E prompts, for
      the "same demand, six lexes" showcase)

Writes: lexis/v2/viz/data.json
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from math import comb
from pathlib import Path

# Overridable so the static-site export can rebuild against the repo checkout.
REPO_ROOT = Path(os.environ.get("LEXIS_REPO_ROOT",
                                Path(__file__).resolve().parents[3]))
WORK_DIR = Path("/home/godli/eval-work/lexis-pilot2")
OUT = Path(__file__).resolve().parent / "data.json"

PILOTS = {
    "pilot1": REPO_ROOT / "lexis" / "results" / "pilot1.jsonl",
    "pilot2": REPO_ROOT / "lexis" / "v2" / "results" / "pilot2.jsonl",
}


def mcnemar_exact(b: int, c: int) -> float:
    m = b + c
    if m == 0:
        return 1.0
    lo = sum(comb(m, k) for k in range(0, min(b, c) + 1)) / 2 ** m
    hi = sum(comb(m, k) for k in range(max(b, c), m + 1)) / 2 ** m
    return min(1.0, lo + hi)


def analyze(path: Path) -> dict:
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    trials: dict[tuple, dict] = defaultdict(dict)
    briefs_by_trial: dict[tuple, list] = {}
    status_by_trial: dict[tuple, str] = {}
    failed_stage: dict[tuple, str | None] = {}
    for r in rows:
        key = (r["topic"], r["role"])
        trials[key][r["arm"]] = r["answer"]
        briefs_by_trial[key] = [b["stage"] for b in r.get("stage_briefs", [])]
        status_by_trial[key] = r["status"]
        failed_stage[key] = r.get("failed_stage")

    topics = sorted({t for t, _ in trials})
    roles = sorted({ro for _, ro in trials})

    cells = []
    pairs = []
    for (topic, role), arms in trials.items():
        lx, nt, ct = arms.get("lexis"), arms.get("neutral_translation"), arms.get("control")
        stage_names = briefs_by_trial[(topic, role)]
        d_retries = sum(1 for s in stage_names if s.startswith("D_retry"))
        dn_retries = sum(1 for s in stage_names if s.startswith("D_neutral_retry"))
        cell = {
            "topic": topic, "role": role,
            "lexis": lx, "neutral": nt, "control": ct,
            "status": status_by_trial[(topic, role)],
            "failed_stage": failed_stage[(topic, role)],
            "d_retries": d_retries, "dn_retries": dn_retries,
        }
        cells.append(cell)
        if lx and nt and ct:
            pairs.append({"flip_lexis": lx != ct, "flip_neutral": nt != ct,
                          "lexis": lx, "control": ct})

    n = len(pairs)
    fl = sum(p["flip_lexis"] for p in pairs)
    fn = sum(p["flip_neutral"] for p in pairs)
    b = sum(p["flip_lexis"] and not p["flip_neutral"] for p in pairs)
    c = sum(p["flip_neutral"] and not p["flip_lexis"] for p in pairs)

    control_by_topic = {}
    for topic in topics:
        seq = [cl["control"] for cl in cells if cl["topic"] == topic and cl["control"]]
        control_by_topic[topic] = seq

    return {
        "n_trials": len(trials),
        "n_complete": n,
        "topics": topics,
        "roles": roles,
        "cells": cells,
        "flips": {
            "lexis": fl, "neutral": fn,
            "lexis_rate": fl / n if n else None,
            "neutral_rate": fn / n if n else None,
            "discordant_lexis_only": b, "discordant_neutral_only": c,
            "mcnemar_p": mcnemar_exact(b, c),
            "yes_to_no": sum(1 for p in pairs if p["lexis"] == "NO" and p["control"] == "YES"),
            "no_to_yes": sum(1 for p in pairs if p["lexis"] == "YES" and p["control"] == "NO"),
        },
        "gate": {
            "d_retried_trials": sum(1 for cl in cells if cl["d_retries"] > 0),
            "dn_retried_trials": sum(1 for cl in cells if cl["dn_retries"] > 0),
            "gate_failed_trials": sum(1 for cl in cells
                                      if (cl["failed_stage"] or "").endswith("_gate")),
        },
        "control_by_topic": control_by_topic,
    }


ARM_FILES = {
    "lexis": "stage_E_lexis",
    "neutral_translation": "stage_E_neutral_translation",
    "control": "stage_E_control",
}


def e_answers() -> dict:
    """Full E response texts per (topic, role, arm), from pilot2 trial dirs.

    A stage_E_<arm>_retry file means the first call crashed (infra); the retry
    holds the answer that was scored, so it wins when present.
    """
    out: dict[str, dict] = {}
    for bundle_path in sorted(WORK_DIR.glob("trial-*/bundle.json")):
        b = json.loads(bundle_path.read_text())
        tdir = bundle_path.parent
        arms = {}
        for arm, stem in ARM_FILES.items():
            retry = tdir / f"{stem}_retry.raw.txt"
            first = tdir / f"{stem}.raw.txt"
            path = retry if retry.exists() else first
            if path.exists():
                arms[arm] = {"text": path.read_text(), "retried": retry.exists()}
        out[f"{b.get('topic')}\u0000{b.get('role')}"] = arms
    return out


def model_pin(path: Path) -> dict:
    """Exact model IDs observed in the claude -p JSON envelopes, by stage kind."""
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    seen: dict[str, set] = {"E": set(), "GATE": set(), "A-D": set()}
    for r in rows:
        briefs = list(r.get("stage_briefs", []))
        if r.get("e_brief"):
            briefs.append(r["e_brief"])
        for brf in briefs:
            kind = ("GATE" if brf["stage"].startswith("GATE") else
                    "E" if brf["stage"].startswith("E_") else "A-D")
            for mid in brf.get("model_versions") or []:
                seen[kind].add(mid)
    return {k: sorted(v) for k, v in seen.items()}


def showcase(topic: str = "veganism") -> list[dict]:
    """The same pinned demand rendered in every role's lexis (from pilot2 bundles)."""
    out = []
    for bundle_path in sorted(WORK_DIR.glob("trial-*/bundle.json")):
        b = json.loads(bundle_path.read_text())
        if b.get("topic") != topic:
            continue
        out.append({
            "role": b.get("role"),
            "lexis_prompt": b["e_prompts"].get("lexis"),
            "neutral_prompt": b["e_prompts"].get("neutral_translation"),
            "control_prompt": b["e_prompts"].get("control"),
        })
    out.sort(key=lambda x: x["role"] or "")
    return out


def main() -> None:
    topics_bank = [json.loads(l) for l in
                   (REPO_ROOT / "lexis/v2/topics/approved.jsonl").read_text().splitlines()
                   if l.strip()]
    roles_bank = [json.loads(l) for l in
                  (REPO_ROOT / "lexis/v2/roles/approved.jsonl").read_text().splitlines()
                  if l.strip()]
    data = {
        "pilots": {name: analyze(path) for name, path in PILOTS.items()},
        "models": model_pin(PILOTS["pilot2"]),
        "e_answers": e_answers(),
        "showcase_topic": "veganism",
        "showcase": showcase("veganism"),
        "topic_bank": [{"topic": t["topic"], "demand": t["demand"],
                        "truth_conditions": t.get("truth_conditions")} for t in topics_bank],
        "role_bank": [{"role": r["role"], "register_notes": r.get("register_notes")}
                      for r in roles_bank],
    }
    OUT.write_text(json.dumps(data, indent=1))
    p2 = data["pilots"]["pilot2"]
    print(f"wrote {OUT} — pilot2: {p2['n_complete']} complete, "
          f"lexis flips {p2['flips']['lexis']}, neutral {p2['flips']['neutral']}, "
          f"p={p2['flips']['mcnemar_p']:.3f}, showcase roles={len(data['showcase'])}")


if __name__ == "__main__":
    main()

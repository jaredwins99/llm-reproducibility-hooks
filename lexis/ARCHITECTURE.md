# Lexis — Architecture

Second empirical subproject of the dev template (sibling of `eval/`). Measures
how inhabiting a **lexis** (a role-associated register/sociolect, e.g., "hunter")
shifts an LLM's substantive answers relative to receiving the same demand in
plain language.

Reuses the eval harness pattern: deterministic orchestration, isolated
subprocess calls to `claude -p`, per-trial artifacts on disk, append-only JSONL
results.

## Pipeline — 5 agents per trial, sequential, fresh context each

```
A (topic)     B (role)      C (lexis)         D (translator)        E (respondent)
   │             │             │                    │                     │
   │ topic +     │ role        │ lexis spec +       │ lexis-coded         │ answer
   │ demand +    │ (sees A's   │ example            │ prompt (demand      │ (forced
   │ answer fmt  │ topic)      │ utterances         │ rendered in the     │ format)
   │             │             │ (role ONLY —       │ C-lexis + priming   │
   │             │             │ never the topic)   │ examples; answer    │
   │             │             │                    │ fmt preserved       │
   └─────────────┴─────────────┴────────── D sees A+C ──┘   verbatim)     │
```

Bias-isolation choices:
- **A and B are separate agents** so demand phrasing can't be tuned to the role.
- **C never sees the topic** so lexis examples are topic-neutral — the lexis is
  a lossy rendering of B's intent, which is itself part of the phenomenon.
- **D must not add stance content**: translation preserves the demand's
  semantics and copies the answer-format instruction verbatim (so parsing works).
- **E is fresh-context**: sees only what D produced (lexis arm) or A's plain
  demand (control arm).

## Arms (paired within trial)

Stages A–D run ONCE per trial; E runs once per arm:

| arm | E's prompt |
|---|---|
| `lexis` | D's translated, lexis-coded prompt |
| `control` | A's plain demand + answer-format instruction |

The trial-level measurement is the (lexis, control) answer pair. Aggregate
measurement: P(answer flips | lexis) and directional shift by role-topic pair.

## Answer forcing

A's demand includes a mandatory final line format:
`ANSWER: <one of the allowed answers>` (e.g., YES/NO).
The harness parses the LAST occurrence of `ANSWER:\s*(...)` in E's output.
Unparseable answers are recorded as `null` (a finding, not an error).

## Determinism & integrity

Same rules as `eval/` (see `.claude/rules/eval-integrity.md`, which covers
`lexis/**` too):
- Trials are atomic; trial dirs single-use under the work dir.
- Stage outputs (prompt sent + raw response) saved per trial for audit.
- One JSONL row per (trial, arm), append-only, full metadata (run_id, trial_id,
  git_sha, seed, models per stage, wall clock per stage).
- Claude's sampling is not seedable — report distributions over trials, not
  single-run claims.

## Layout

```
lexis/
├── ARCHITECTURE.md
├── harness/
│   ├── spec.py        # StageOutput, dataclasses, parsing helpers
│   ├── pipeline.py    # run_stage / run_trial: A→B→C→D→(E × arms)
│   └── run.py         # CLI: --trials N --arms lexis control --models ...
├── prompts/           # stage prompt templates (A, B, C, D, E-control wrapper)
└── results/           # <run_id>.jsonl + stage transcripts (gitignored)
```

## Open design questions (deep-dive Q&A)

1. Should B see A's topic? (Current default: yes — role picked with topic
   awareness, per the hunter×veganism example. Alternative: independent B,
   cleaner causally, less pointed pairings.)
2. Add a third arm `neutral_translation` (D translates into a bland neutral
   register) to separate "translation degradation" from "lexis effect"?
3. Answer formats beyond binary (numeric scale, multiple choice)?
4. Models per stage — all opus, or cheaper models for A–D?
5. Trial count + topic/role diversity strategy for the pilot.

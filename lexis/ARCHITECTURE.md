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
| `neutral_translation` | D's rewording of the demand into a bland institutional register (same lossy translation process, no lexis) — separates "any thorough rewording shifts answers" from "the lexis does" |
| `control` | A's plain demand + answer-format instruction |

The trial-level measurement is the (lexis, neutral_translation, control) answer
triple. Aggregate: P(answer flips | lexis) vs P(flips | neutral rewording), and
directional shift by role-topic pair.

## Vetted topic bank

Topics are human-vetted before use (contentiousness, neutrality, answerability):

1. `python -m lexis.harness.gen_topics --n 30` → stage-A candidates to
   `lexis/topics/candidates.jsonl`
2. Human review → approved lines copied to `lexis/topics/approved.jsonl`
3. `run.py` draws from the approved bank by default (`--live-topics` opts out)

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

## Resolved design decisions (deep-dive Q&A, 2026-04)

1. **B never sees A's topic** — independent role choice, steered by a rotating
   `role_hint` for diversity. Cleaner causal reading; inert pairings accepted.
2. **Three arms** including `neutral_translation` (see Arms above).
3. **Answer format**: binary YES/NO for the pilot (parser already supports any
   closed answer set).
4. **Models**: sonnet for stages A–D (generation), opus for E (the measured
   respondent). Per-stage `--model-x` flags exist for later variation, e.g.
   re-running the same A–D artifacts with E ∈ {opus, sonnet, haiku}.
5. **Pilot**: 10 trials from the vetted topic bank.

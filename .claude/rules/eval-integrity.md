---
description: Experimental integrity rules for the eval harness — these protect the A/B test from confounds
paths:
  - "eval/**/*"
  - "ongoing_issues.md"
  - "FELLOWSHIP_PITCH.md"
---

# Eval Integrity

These rules exist because the fellowship pitch hinges on the harness producing trustworthy A/B results. Violating any of these silently invalidates conclusions.

## Atomic trials
- A trial is one complete run: materialize dir → run Claude → score → record → destroy dir.
- Never modify a trial directory after Claude starts.
- If a trial crashes mid-run, record the crash as a result (`status: "crashed", error: "..."`). Do NOT retry in place. Do NOT silently discard.

## Byte-identical task prompts
- The task prompt given to with-refs and without-refs variants MUST be byte-for-byte identical.
- The only difference between variants is the CONTENTS of the trial directory (rules, hooks, reference/, permissions) — never the prompt itself.

## No contamination between variants
- Trial directories are single-use. Create fresh under `/tmp/eval-<run_id>/trial-<n>/`, never reuse.
- Never run trials under `dev_template/` — parent `CLAUDE.md`/rules would leak in.
- The without-refs variant must contain NO `.claude/` directory, NO `CLAUDE.md`, NO symlinks or paths to the reference library.
- The with-refs variant gets the reference library hard-linked inside the trial dir, never by symlink or external path.

## Scorer isolation
- The scoring code must not read the reference library. If the scorer accidentally uses refs, it could reward ref-shaped outputs regardless of actual quality.
- Scorer inputs are restricted to: the task spec, the agent's output files (stan model, python code, logs), and objective tool output (did it compile, did Stan sampler finish, what were the diagnostics).

## Append-only results
- Every trial appends one JSON line to `eval/results/<run_id>.jsonl`.
- Never rewrite or edit prior lines. If analysis requires transforming results, produce a derived file.
- Each line records full metadata: `timestamp, git_sha, python_version, claude_version, wall_clock_s, task_id, variant, model, seed, status, metrics, outputs_path`.

## Reproducibility
- Seed every seedable randomness source: numpy, Stan data-generation, Python `random`. Log the seed per trial.
- What we cannot seed: Claude's own sampling. Report mean ± variance across trials; never claim single-run results are reproducible.
- Record the git SHA of `dev_template/` at trial start. If uncommitted changes exist, refuse to run.

## No harness-logic branching on variant content
- Harness code should branch on "which variant am I running" only when materializing the trial directory.
- Scoring, logging, result format, metrics — all variant-agnostic. If scoring uses `if variant == 'with_refs'`, that's a bug.

## What we do not measure
- Code elegance, LOC, subjective quality. These introduce bias.
- Agent verbosity beyond token counts.
- Whether the agent followed the protocol "correctly" as a separate metric (exception: we may log it for the writeup, but it does not influence outcome metrics).

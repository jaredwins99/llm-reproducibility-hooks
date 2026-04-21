# Ongoing Issues & Design Decisions

Tracks open design questions, confounds, and commitments for the Stan proof of concept and eval harness. Living document — update as decisions are made or new issues surface.

## Resolved decisions

### Unit of measurement
**Decision**: we measure the *system* (reference library + protocol + rule + hook + search tooling), not "having references" in isolation.

**Implication**: conclusions are about the *package* of reference-forcing, not about any individual component. We cannot claim "the rule did it" or "the hook did it" — only that the system collectively changes outcomes.

### Variant isolation
**Decision**: "isolated Claude" approach.

- **Without-refs variant**: a freshly created task directory containing only the problem files. No `CLAUDE.md`, no `.claude/` dir, no rules, no skills, no hooks. Claude Code runs in this directory with default base behavior. WebFetch and WebSearch remain allowed (that's the base Claude capability we're comparing against).
- **With-refs variant**: same task directory, plus the reference library accessible inside it, plus the `stan.md` rule, plus the `.stan` hook, plus search.sh in the permissions allowlist.

The manipulation is: does adding the full reference-forcing package improve outcomes vs Claude using its training data + web search alone?

### What counts as "outside the problem folder"
**Decision**: nothing outside the task directory is accessible. No parent `CLAUDE.md`, no symlinks to outside resources. Everything the agent can reach must be inside the trial's working directory.

**Implication**: the reference library, when present, must be *inside* the task directory. Approaches:
- Hard-link (`cp -al`) the shared reference tree into each with-refs trial. Fast, no disk overhead, not a symlink.
- Full copy. Reliable but wasteful (26MB × N trials).
- Recommended: hard-link.

### Scoring scope
**Decision**: Stan-specific scorers now. Generic `Scorer` interface later when we add cross-domain tasks. Don't prematurely abstract.

### Partial runs
**Decision**: trials are atomic. Stan doesn't support checkpointing mid-sampling, so any crashed trial is discarded. JSONL append-only still applies at the *between-trial* level — completed trial results are never lost.

## Metrics (per trial)

Working set, for review:

1. **Prediction accuracy** — posterior predictive check quality (distance between observed and replicated statistics)
2. **Parameter recovery** — fraction of true parameters within 90% credible intervals
3. **Time complexity** — wall-clock (compile + sample), sampling seconds, ESS per second
4. **Memory complexity** — peak RSS during sampling, Stan's reported memory
5. **Iterations to working state** — how many attempts before compiles + fits cleanly (Agent A's first test: 1 attempt. Agent B: 7 attempts.)
6. **Sampling diagnostics** — divergence count, R-hat max, minimum ESS
7. **Token usage** — if obtainable from Claude Code logs (cost proxy, also a capability signal)
8. **Did it use the protocol correctly?** (with-refs only) — did the agent actually run search.sh before writing, or did it ignore the rule/hook?

Open question: are we missing any signal? Notably *not* measuring:
- Code elegance / LOC / cyclomatic complexity (subjective, low signal)
- Warning counts beyond divergences (noise)

## Open design issues

### 1. Confounds from Claude's base behavior
Even in without-refs, Claude may use `WebFetch` or `WebSearch` to find Stan docs online, or recall training data effectively. This is accepted — it's the baseline we're comparing against.

However: **if a model's training cutoff is later than ours, or the model is better at web-grounding, the gap might close not because refs stop helping but because the baseline got stronger.** Worth mentioning in any writeup.

### 2. Statistical power at planned N
At N=10 trials per (variant × model × task) cell, binary outcomes (compiles/doesn't, fits/doesn't) have limited power. For continuous metrics (parameter recovery rate, time), paired tests (Wilcoxon signed-rank) are stronger.

Plan: collect N=10 as baseline. If effects are borderline, expand to N=20 for that cell specifically. Commit to a trial budget before starting (proposal: 600 trial-hours total).

### 3. Task bank composition
Need 20 statistics problems spanning difficulty and domain. Candidates:
- Hierarchical regression (easy, baseline)
- Mixture models with label-switching (medium)
- Gaussian processes (hard, Stan-specific function signatures matter)
- ODE-based models (hard, ODE interfaces matter)
- State-space / HMM (medium)
- Survival with censoring (medium)
- IRT / multilevel IRT (medium)
- Zero-inflated / hurdle (medium)
- Spatial (CAR/ICAR/GP-spatial) (hard)
- Time series (GARCH/INGARCH) (medium-hard)

Need coverage across families AND across the kind of mistakes Claude makes (syntax gotchas, parameterization, numerical stability, prior choice).

Open: who writes the 20 problems? They need ground-truth parameters + data generators + objective scoring. This is real work.

### 4. Model switching
`claude -p --model opus|sonnet|haiku` should work but untested. Need to verify per-call model switching actually works from the CLI before building around it. Fallback: set the default model via env var per trial.

### 5. Compute budget
At N=10 × 3 models × 2 variants × 20 tasks = 1200 trials × ~5 min = **100 hours wall clock** per full sweep, sequentially. Parallelism helps but Claude Code sessions are heavyweight. Worth establishing a daily budget and running incrementally.

### 6. Template-to-pool coupling (future debt)
The template's `stan.md` rule hardcodes `reference/stan/search.sh` as a relative path. When someone scaffolds an external project, that path breaks. Not urgent — the proof of concept lives in this repo where the path resolves. Fix later (config variable, env var, or post-scaffold hook).

### 7. Harness reproducibility
Each trial invokes Claude Code, which is non-deterministic even at temperature=0 (tool ordering, model sampling). Report mean ± variance across trials, not single-run claims. Seed where possible, but don't over-claim reproducibility.

## Deliberately deferred

- Cross-domain tasks (pandas, numpy) — after Stan
- Generic `Scorer` interface — after Stan
- Template-as-external-scaffold path resolution — after proof of concept
- SDK-based runner — after API access

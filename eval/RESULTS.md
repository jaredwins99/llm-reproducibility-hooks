# Eval Results

Findings from running the harness. Each pilot is a section. Most recent at the top.

---

## Pilot 1 — INGARCH, with vs without refs, Opus only (2026-04-21)

### Summary

Running reference-access vs no-reference-access on a multilevel zero-inflated INGARCH task with two prompt styles (minimal and detailed). 12 trials on claude-opus-4-7.

**Headline finding**: reference access helps when the task prompt pins the model specification (detailed). Reference access *hurts* when the prompt leaves model-class choice open (minimal), because the reference library biases Claude toward "textbook" parameterizations that may not match the data-generating process.

### Setup

- **Model**: `claude-opus-4-7`
- **Tasks**: `stan.ingarch.minimal` (open spec), `stan.ingarch.detailed` (additive DGP pinned)
- **Variants**:
  - `without_refs`: fresh trial directory with only `data.json` + `task.md`. No `.claude/`, no reference library. Base Claude behavior.
  - `with_refs`: same + `.claude/rules/stan.md` (mandatory two-track search protocol) + `.claude/settings.json` (PreToolUse hook running `search.sh` on `.stan` edits) + hard-linked `reference/stan/` (733 files).
- **DGP**: additive INGARCH(7,7) with 8 groups, 300 timepoints, zero-inflated. Seed 42, generated once.
- **Scorer**: compiles Claude's `model.stan`, fits on fixed data (500 warmup + 500 sampling, 4 chains, adapt_delta=0.95), records diagnostics + recovery + PPC.
- **Role resolution**: judge-primary (haiku `claude -p` reads model.stan and outputs role→Stan-name mapping). All 12 trials used the judge path; all 12 trials had `params.json` declared by the main Claude.
- **Trials per cell**: 3

### Results

| task | variant | N | compile | fits | cov₉₀ | RMSE | interval_score | divergences | max R̂ | wall |
|---|---|---|---|---|---|---|---|---|---|---|
| `ingarch.detailed` | **with_refs** | 3 | 3/3 | 3/3 | **0.944** | **0.074** | **0.169** | 0.3 | 1.009 | 35s |
| `ingarch.detailed` | without_refs | 3 | 3/3 | 3/3 | 0.815 | 0.110 | 0.420 | 0.3 | 1.012 | 26s |
| `ingarch.minimal` | with_refs | 3 | 3/3 | 3/3 | 0.722 | 0.862 | 5.240 | **470** | — | 49s |
| `ingarch.minimal` | **without_refs** | 3 | 3/3 | 3/3 | **0.796** | **0.190** | **0.722** | 0.0 | 1.409 | 26s |

All 12 trials compiled and fit (no subprocess crashes, no compilation failures).

### What Claude actually built

On the **detailed** prompt, both variants produced structurally similar additive INGARCH models using a Dirichlet-simplex trick to enforce stationarity (`ab_simplex ~ dirichlet(rep_vector(1.0, P + Q + 1))`). With-refs trials were more consistent across repeats (tighter clustering around cov=0.94); without-refs trials ranged 0.56–0.94.

On the **minimal** prompt:

- **with_refs** (all 3 trials nearly identical): **log-linear INGARCH** — `log_lambda[t] = α + Σβ·log1p(y[t-p]) + Σγ·log_lambda[t-q]`. Unconstrained β, γ with `normal(0, 0.5)` priors. The log-linear recursion has no stability constraint and can explode/collapse, causing ~498 divergences per trial. This is the Fokianos/Tjøstheim form, the "modern" textbook parameterization.
- **without_refs**: **additive INGARCH** — `lambda[t] = exp(α) + Σβ·y[t-p] + Σγ·λ[t-q]` with β, γ ∈ [0, 1] via `beta(1, 5)` priors. Matches the DGP. 0 divergences. This is the classical Brannas/Hellstrom form.

### Interpretation

Three compatible readings:

1. **Refs help with specified tasks.** On the detailed prompt (additive DGP pinned), refs reduce interval score by 60% and raise coverage by 13 percentage points. Clean effect; likely replicates.

2. **Refs encode corpus bias toward textbook forms.** On the minimal prompt, refs consistently push Claude toward the log-linear form — likely because academic references emphasize it as the "generalized" formulation. Without refs, Claude picks a simpler additive form. When the DGP is additive, this bias *harms* fit. The effect is structural, not statistical: all three with_refs trials independently chose the same problematic form.

3. **The direction of effect is confounded with DGP choice.** Our DGP is additive. If we had simulated from a log-linear DGP, the reference-induced bias toward log-linear would likely *help* on the minimal prompt. The headline finding that "refs hurt on open prompts" is actually "refs hurt when reference-corpus bias diverges from the DGP."

4. **Refs collapse output variance across trials.** Within-cell standard deviation of coverage was **0.000** for both with_refs cells (identical across 3 trials) vs 0.20+ for both without_refs cells. Trial-to-trial `.stan` files were not byte-identical — Claude wrote different code each time — but consistently chose the same model class, same constraints, same priors. Refs push Claude toward canonical forms and suppress exploration. This is good for reproducibility (with-refs is more predictable) but amplifies bias: when the canonical form is wrong for the data, every trial consistently bakes in that wrongness. Related to literature on mode collapse under grounding/RLHF.

### Limitations

- **N=3 per cell.** Individual cell estimates have wide error bars. The minimal/with_refs cell's near-identical results across three trials suggest Claude is *systematically* choosing the log-linear form rather than randomly — but this needs larger N to confirm.
- **Single DGP family** (additive INGARCH). The confound interpretation (3) cannot be tested without a second DGP family.
- **Single model** (Opus). The differential may depend on model size — smaller models may be more susceptible to ref-induced bias, or less.
- **Judge path unvalidated at scale.** All 12 trials resolved via the judge (haiku). Judge output was sensible in spot-checks but not systematically audited. If the judge systematically mislabels, recovery metrics would be misleading in a correlated way.
- **params.json always produced.** All 12 trials produced params.json. We didn't test the judge-over-wrong-params fallback path in this pilot.

### Planned next: confound test

Add `stan.ingarch.loglinear` as a second task with a log-linear DGP (same model family, different data-generating mechanism). Run the same 2×2×3 pilot. Predict: on the minimal prompt, with_refs should now *help* (because the reference corpus bias matches the DGP). If the prediction holds, it confirms interpretation (3) and makes the finding much more publishable: "reference grounding improves when the corpus bias aligns with ground truth, and hurts when it doesn't."

### Reproducibility

- Results: `eval/results/pilot1.jsonl` (gitignored due to size; key rows above)
- Trial directories: `/tmp/eval-pilot1/trial-*` (preserved with `--keep-dirs`)
- Task definitions: `eval/tasks/stan/ingarch.py` (commit `07e0217` at pilot time)
- Reference library: `reference/stan/` @ `e5b7d9e` (2025-04-30)
- Run command: `python -m eval.harness.run --tasks stan.ingarch.minimal stan.ingarch.detailed --models opus --variants without_refs with_refs --trials-per-cell 3 --claude-bin claude --keep-dirs --run-id pilot1`

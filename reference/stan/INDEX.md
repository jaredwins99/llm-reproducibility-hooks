# Stan Reference Index

Docs: Stan 2.38 (scraped 2026-03-31)
Example-models: stan-dev/example-models @ e5b7d9e (2025-04-30, scraped 2026-04-02)
Total: 733 files (172 docs + 561 models), ~26.6MB

## Source Hierarchy

```
Class 1 — Official Docs (131 files)          ← language spec, function signatures, modeling guide
Class 1b — Example Models (561 .stan files)   ← complete, runnable models from Stan team
Class 2 — Case Studies & Packages (31 files)  ← worked examples, diagnostics, visualization
Class 3 — Community (8 files)                 ← forum distillations, verify against Class 1
```

Trust order: 1 = 1b > 2 > 3. If Class 3 contradicts Class 1, Class 1 wins.

## Search Protocol

Two-stage: **list** then **read**.

```bash
# Stage 1 — find relevant files (cheap, returns filenames only)
bash reference/stan/search.sh --list "query"

# Stage 2 — read the best matches in full (use Read tool on specific files)
#   For .stan files: always read the whole file (most are <60 lines)
#   For docs: read the whole file or use --read for top 3 with context

# Other modes
bash reference/stan/search.sh "query"              # grep excerpts, all classes
bash reference/stan/search.sh --read "query"        # full content, top 3 files
bash reference/stan/search.sh --class 1b "query"    # example models only
bash reference/stan/search.sh --from-file model.stan # extract concepts from code
```

Typical agent workflow:
1. `--list "gaussian process poisson"` → see 20 candidate files
2. Pick the closest example model (e.g., `gp-fit-pois.stan, 39L`)
3. Read it in full — it IS the reference
4. Also read the relevant docs chapter if needed (e.g., `users-guide/gaussian-processes.md`)
5. Write the model

## Class 1 — Official Docs

| Directory | What | Files |
|---|---|---|
| `users-guide/` | Modeling guide — GPs, mixtures, ODEs, hierarchical, missing data, etc. | 38 |
| `reference-manual/` | Language spec — blocks, types, expressions, inference algorithms | 23 |
| `functions-reference/` | Every built-in function, distribution, and math operation | 32 |
| `cmdstan-guide/` | Command-line interface — flags, arguments, output formats | 22 |
| `cmdstanr/` | R interface — sampling, optimization, variational inference | 8 |
| `cmdstanpy/` | Python interface — sampling, optimization, variational inference | 8 |

## Class 1b — Example Models

561 complete `.stan` files from `stan-dev/example-models`. Compilation-verified by Stan CI.

| Directory | What | .stan |
|---|---|---|
| `example-models/misc/gaussian-process/` | GP fit, predict, simulate — Poisson, logit, multi-output, ARD, Cholesky | 14 |
| `example-models/misc/hmm/` | Hidden Markov models — standard, analytic, semi-supervised | 4 |
| `example-models/misc/irt/` | Item response theory — 1PL, 2PL, multilevel | 4 |
| `example-models/misc/cluster/` | Mixtures — soft K-means, LDA, naive Bayes | 5 |
| `example-models/misc/garch/` | Time series — ARCH, GARCH(1,1), Koyck | 3 |
| `example-models/misc/dlm/` | Dynamic linear models, state-space | 3 |
| `example-models/misc/ecology/` | Mark-recapture, occupancy | 6 |
| `example-models/ARM/` | Applied Regression Modeling (Gelman & Hill), 21 chapters | 161 |
| `example-models/BPA/` | Bayesian Population Analysis — CJS, multistate, integrated | 69 |
| `example-models/bugs_examples/` | Classic BUGS translations, 3 volumes | 76 |
| `example-models/knitr/` | Case study code — CAR-Poisson, IRT, pest-control, golf, ODEs | 131 |
| `example-models/jupyter/` | COVID, radon, sum-to-zero | 20 |
| `example-models/education/` | Causal inference, IRT teaching | 14 |
| `example-models/basic_*/` | Distribution and estimator fundamentals | 21 |
| `example-models/Bayesian_Cognitive_Modeling/` | Signal detection, memory, psychophysics | 7 |

## Class 2 — Case Studies & Packages

| Directory | What | Files |
|---|---|---|
| `case-studies/` | Divergences, mixtures, GPs, ODEs, spatial, hierarchical, splines | 16 |
| `bayesplot/` | MCMC visualization, diagnostics plots, PPCs | 4 |
| `loo/` | PSIS-LOO cross-validation, model comparison, stacking | 7 |
| `posterior/` | Draw formats, summaries, diagnostics | 2 |
| `math-library/` | Stan Math — autodiff, C++ backend | 1 |
| `compiler/` | stanc3 — compilation phases, AST, MIR | 1 |

## Class 3 — Community

| Directory | What | Files |
|---|---|---|
| `forum/` | Divergent transitions primer, prior recommendations, reparameterization, warnings, performance | 8 |

---
description: Stan modeling — mandatory reference lookup before writing Stan code
globs: ["**/*.stan", "**/*stan*"]
---

# Stan Reference Protocol

733 files in `reference/stan/`. See `reference/stan/INDEX.md` for full inventory.
Version: Stan 2.38 docs + stan-dev/example-models @ e5b7d9e (2025-04-30).

## Source Hierarchy

```
Class 1  — Official Docs (131 files)      ← language spec, functions, modeling guide
Class 1b — Example Models (561 .stan)      ← complete runnable models from Stan team
Class 2  — Case Studies & Packages (31)    ← worked examples, diagnostics, visualization
Class 3  — Community (8 files)             ← forum distillations, verify against Class 1
```

Trust: 1 = 1b > 2 > 3. Class 3 contradicts Class 1 → Class 1 wins.

## Mandatory Search — Two Parallel Tracks

BEFORE writing or editing ANY `.stan` file, search BOTH tracks:

**Track A — Docs** (rules, signatures, parameterization advice):
```bash
bash reference/stan/search.sh --list "your concept"         # find relevant doc pages
# Then Read the top doc file for rules/priors/syntax
```

**Track B — Examples** (complete working models to pattern-match):
```bash
bash reference/stan/search.sh --class 1b "your concept"     # find matching .stan files
# Then Read the closest example model in full (most are <60 lines)
```

For existing files, also run:
```bash
bash reference/stan/search.sh --from-file model.stan         # auto-extract concepts
```

Pick the top 2-3 from each track. Read them. Then write.

NEVER write Stan code from memory. ALWAYS search first.

## Common Searches

| Concept | Track A (docs) query | Track B (examples) to read |
|---|---|---|
| GP | `"gaussian process gp_exp_quad_cov"` | `example-models/misc/gaussian-process/gp-fit-pois.stan` |
| Mixture | `"finite mixture log_sum_exp"` | `example-models/misc/cluster/` |
| Hierarchical | `"hierarchical reparameterization"` | `example-models/misc/eight_schools/` |
| HMM | `"hmm_marginal hidden markov"` | `example-models/misc/hmm/` |
| IRT | `"item response"` | `example-models/misc/irt/` |
| ODE | `"ode_rk45 ode_bdf"` | `example-models/knitr/lotka-volterra/` |
| Zero-inflated | `"zero inflated hurdle"` | `example-models/BPA/Ch.12/` |
| Survival | `"survival censored"` | `example-models/BPA/Ch.07/` |
| Spatial | `"car icar spatial"` | `example-models/knitr/car-iar-poisson/` |
| Time series | `"time series autoregressive"` | `example-models/misc/garch/` |
| Missing data | `"missing data"` | — |
| Array/matrix ops | `"multi-indexing array matrix"` | — |
| User functions | `--class 1 "user functions"` | — |
| CmdStanR | `--class 1 "cmdstanr sample"` | — |
| CmdStanPy | `--class 1 "cmdstanpy sample"` | — |
| Divergences | `"divergent reparameterization"` | also read `forum/warning_messages_explained.md` |

## Rules (empirically validated)

- Non-centered parameterization for hierarchical models unless data is very informative
- Never `uniform` priors — use weakly informative (e.g., `inv_gamma(5,5)` for GP lengthscales)
- Don't hard-bound hyperparameters (`<lower=0.5>`) — let priors handle it
- `target +=` with `log_sum_exp` for marginalizing discrete parameters
- `poisson_log` not `poisson(exp(...))`, `bernoulli_logit` not `bernoulli(inv_logit(...))`
- `cholesky_decompose` + `multi_normal_cholesky` for N > 20, never raw `multi_normal`
- Add jitter (1e-6 to 1e-9) to GP covariance diagonals

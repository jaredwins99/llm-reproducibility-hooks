---
description: Stan modeling — mandatory reference lookup before writing Stan code
globs: ["**/*.stan", "**/*stan*"]
---

# Stan Code Rules

## Reference Material Classes

The `reference/stan/` directory contains documentation in three priority classes:

- **Class 1 — Official Docs** (users-guide, reference-manual, functions-reference, cmdstan-guide, cmdstanr, cmdstanpy): Ground truth. Always search first. Follow exactly.
- **Class 2 — Case Studies & Packages** (case-studies, math-library, compiler, bayesplot, loo, posterior): Worked examples and supporting tools. Search when Class 1 doesn't answer.
- **Class 3 — Community** (forum): Tips and troubleshooting. Search last. If it contradicts Class 1, Class 1 wins.

Version: Stan 2.38. See `reference/stan/INDEX.md` for full inventory.

## Mandatory Search Protocol

BEFORE writing or editing ANY `.stan` file, you MUST:

1. Run `bash reference/stan/search.sh --from-file <the_stan_file>` if the file already exists
2. Run `bash reference/stan/search.sh "<relevant_concept>"` for the modeling approach
3. Read the returned reference material. Class 1 results are authoritative. Follow them exactly.
4. If unsure, search a specific class: `bash reference/stan/search.sh --class 1 "topic"`

NEVER write Stan code from memory. ALWAYS search first.

## Common Searches

- Regression: `search.sh "regression"`
- Hierarchical: `search.sh "hierarchical reparameterization"`
- Time series: `search.sh "time series autoregressive"`
- Mixture models: `search.sh "finite mixture log_sum_exp"`
- Missing data: `search.sh "missing data"`
- GP: `search.sh "gaussian process"`
- Survival: `search.sh "survival censored"`
- Zero-inflated: `search.sh "zero inflated hurdle"`
- ODE: `search.sh "ode"`
- Divergences: `search.sh "divergent reparameterization non-centered"`
- Array/matrix ops: `search.sh "multi-indexing array matrix"`
- Functions: `search.sh --class 1 "user functions"`
- CmdStanR: `search.sh --class 1 "cmdstanr sample"`
- CmdStanPy: `search.sh --class 1 "cmdstanpy sample"`

## Common Mistakes to Avoid
- Always use non-centered parameterizations for hierarchical models unless data is very informative
- Never use `uniform` priors — use proper weakly informative priors
- Use `target +=` for custom log-density, not sampling statements when marginalizing
- Use `log_sum_exp` for mixture models, never raw `exp`
- For warnings: `search.sh "divergent"` or read `forum/warning_messages_explained.md`

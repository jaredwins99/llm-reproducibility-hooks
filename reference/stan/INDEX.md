# Stan Reference Index

Version: Stan 2.38 (scraped 2026-03-31)

## Class 1 — Official Reference (always search first)

| Directory | What | Files |
|---|---|---|
| `users-guide/` | Stan User's Guide — models, techniques, examples | 38 |
| `reference-manual/` | Stan Reference Manual — language spec, inference algorithms | 23 |
| `functions-reference/` | Stan Functions Reference — all built-in functions, distributions, math | 12+ |
| `cmdstan-guide/` | CmdStan Guide — command-line interface | TBD |
| `cmdstanr/` | CmdStanR — R interface API, vignettes | 8 |
| `cmdstanpy/` | CmdStanPy — Python interface API, vignettes | 8 |

## Class 2 — Case Studies & Supporting Packages (search when Class 1 doesn't answer)

| Directory | What | Files |
|---|---|---|
| `case-studies/` | Official case studies — worked examples with full code | TBD |
| `math-library/` | Stan Math Library — autodiff, C++ backend | TBD |
| `compiler/` | stanc3 compiler — internals, optimization | TBD |
| `bayesplot/` | bayesplot — visualization for MCMC diagnostics | TBD |
| `loo/` | loo — LOO cross-validation, model comparison | TBD |
| `posterior/` | posterior — working with posterior draws | TBD |

## Class 3 — Community Knowledge (search last, verify against Class 1)

| Directory | What | Files |
|---|---|---|
| `forum/` | Stan Discourse — common issues, tips, troubleshooting | 8 |

## Search Priority

The search script (`search.sh`) returns results in this order:
1. Class 1 directories first (official docs)
2. Class 2 directories second (case studies, packages)
3. Class 3 directories last (forum)

When Class 3 material contradicts Class 1, Class 1 wins.

# Stan Reference Index

Version: Stan 2.38 (scraped 2026-03-31)
Total: 172 files, ~1.6MB

## Class 1 — Official Reference (always search first)

| Directory | What | Files |
|---|---|---|
| `users-guide/` | Stan User's Guide — models, techniques, examples | 38 |
| `reference-manual/` | Stan Reference Manual — language spec, inference algorithms | 23 |
| `functions-reference/` | Stan Functions Reference — all built-in functions, distributions, math | 32 |
| `cmdstan-guide/` | CmdStan Guide — command-line interface, all flags and options | 22 |
| `cmdstanr/` | CmdStanR — R interface API, vignettes, posterior draws | 8 |
| `cmdstanpy/` | CmdStanPy — Python interface API, sampling, optimization, VI | 8 |

## Class 2 — Case Studies & Supporting Packages (search when Class 1 doesn't answer)

| Directory | What | Files |
|---|---|---|
| `case-studies/` | Official case studies — divergences, mixtures, GPs, ODEs, spatial, hierarchical | 16 |
| `bayesplot/` | bayesplot — MCMC visualization, diagnostics plots, PPCs | 4 |
| `loo/` | loo — PSIS-LOO cross-validation, model comparison, stacking | 7 |
| `posterior/` | posterior — draw formats, summaries, diagnostics functions | 2 |
| `math-library/` | Stan Math Library — autodiff, C++ backend, dependencies | 1 |
| `compiler/` | stanc3 compiler — compilation phases, AST, MIR, code modules | 1 |

## Class 3 — Community Knowledge (search last, verify against Class 1)

| Directory | What | Files |
|---|---|---|
| `forum/` | Stan Discourse — divergent transitions primer, priors, reparameterization, warnings | 8 |

## Search

```bash
bash reference/stan/search.sh "query"              # all classes, priority order
bash reference/stan/search.sh --class 1 "query"    # official docs only
bash reference/stan/search.sh --class 2 "query"    # case studies only
bash reference/stan/search.sh --class 3 "query"    # forum only
bash reference/stan/search.sh --from-file model.stan  # auto-extract concepts
```

When Class 3 contradicts Class 1, Class 1 wins.

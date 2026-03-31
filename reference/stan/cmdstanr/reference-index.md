# CmdStanR Function Reference Index (v0.9.0)

## Package Setup & Configuration

- `cmdstanr-package` — CmdStanR: the R interface to CmdStan
- `cmdstanr_global_options` — Settings for package behavior
- `install_cmdstan()`, `rebuild_cmdstan()` — Installation utilities
- `set_cmdstan_path()`, `cmdstan_path()` — Path management

## Model Operations

- `cmdstan_model()` — Creates CmdStanModel objects
- `compile()` — Compiles Stan programs
- `check_syntax()` — Validates Stan code
- `sample()`, `sample_mpi()` — MCMC sampling methods
- `optimize()` — Optimization algorithms
- `variational()` — Variational inference
- `pathfinder()` — Pathfinder algorithm
- `laplace()` — Laplace approximation
- `diagnose()` — Diagnostic analysis
- `generate_quantities()` — Standalone quantities generation

## Results Extraction

- `draws()` — Posterior samples
- `summary()` — Summary statistics
- `sampler_diagnostics()` — MCMC diagnostics
- `log_prob()`, `grad_log_prob()`, `hessian()` — Probability calculations
- `mle()` — Point estimates
- `output_files()`, `save_object()` — File management

## Utility Functions

- `read_cmdstan_csv()` — Import CSV results
- `write_stan_json()`, `write_stan_file()` — Data/code export
- `as_draws()` — Convert to draws objects
- `register_knitr_engine()` — R Markdown integration

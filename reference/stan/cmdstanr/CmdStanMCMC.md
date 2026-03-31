# CmdStanMCMC Objects

## Overview

A `CmdStanMCMC` object represents a fitted model returned by the `$sample()` method of a `CmdStanModel`. These are R6 objects designed to store and access MCMC sampling results.

## Methods by Category

### Extract Contents

- `$draws()` — Posterior draws in posterior package formats
- `$sampler_diagnostics()` — Returns diagnostics as draws_array
- `$lp()` — Total log probability density
- `$inv_metric()` — Inverse metric per chain
- `$init()` — User-specified initial values
- `$metadata()` — Metadata from CSV files
- `$num_chains()` — Chain count
- `$code()` — Stan code as character vector

### Summarize & Diagnose

- `$print()` and `$summary()` — Via `posterior::summarise_draws()`
- `$diagnostic_summary()` — Sampler diagnostics and warnings
- `$cmdstan_summary()` — CmdStan's stansummary tool
- `$cmdstan_diagnose()` — CmdStan's diagnose tool
- `$loo()` — Approximate LOO-CV via `loo::loo.array()`

### Save & Export

- `$save_object()` — Save fitted object
- `$save_output_files()` — Save CSV outputs
- `$save_data_file()` — Save JSON data
- `$save_latent_dynamics_files()` — Save diagnostics

### Report & Access

- `$output()` — stdout/stderr access
- `$time()` — Execution times
- `$return_codes()` — CmdStan exit codes

### Advanced Model Methods

- `$expose_functions()` — Access Stan functions in R
- `$init_model_methods()` — Expose log-probability and gradients
- `$log_prob()`, `$grad_log_prob()`, `$hessian()` — Log-probability computations
- `$constrain_variables()`, `$unconstrain_variables()`, `$unconstrain_draws()` — Parameter transformations
- `$variable_skeleton()` — Restructure parameter vectors

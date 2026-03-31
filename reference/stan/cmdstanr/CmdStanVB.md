# CmdStanVB Objects

## Overview

A `CmdStanVB` object represents the fitted model returned by calling the `$variational()` method on a `CmdStanModel` object.

## Methods by Category

### Extract Contents

- `$draws()` — Approximate posterior draws
- `$lp()` — Log probability density
- `$lp_approx()` — Approximate log probability
- `$init()` — Initial values
- `$metadata()` — Metadata from CSV files
- `$code()` — Stan code as character vector

### Summarization

- `$summary()` — Runs posterior summarization
- `$cmdstan_summary()` — Executes CmdStan's summary tool

### File Operations

- `$save_object()` — Save fitted object
- `$save_output_files()` — Save CSV outputs
- `$save_data_file()` — Save JSON data
- `$save_latent_dynamics_files()` — Save diagnostics

### Diagnostics

- `$time()` — Reports execution duration
- `$output()` — Displays console output
- `$return_codes()` — Provides CmdStan exit codes

### Stan Integration (Advanced)

- `$expose_functions()` — Access Stan functions in R
- `$init_model_methods()` — Expose log-probability and gradients
- `$log_prob()`, `$grad_log_prob()`, `$hessian()` — Log-probability computations
- `$constrain_variables()`, `$unconstrain_variables()`, `$unconstrain_draws()` — Parameter transformations
- `$variable_skeleton()` — Restructure parameter vectors

## Related Objects

- `CmdStanMCMC` — From `$sample()`
- `CmdStanMLE` — From `$optimize()`
- `CmdStanPathfinder` — From `$pathfinder()`
- `CmdStanGQ` — From `$generate_quantities()`
- `CmdStanLaplace` — From `$laplace()`
- `CmdStanDiagnose` — From `$diagnose()`

# cmdstan_model() Function

## Function Signature

```r
cmdstan_model(stan_file = NULL, exe_file = NULL, compile = TRUE, ...)
```

## Purpose

Creates a new `CmdStanModel` object from a Stan program file or existing executable. The object enables model fitting using Stan's various algorithms through dedicated methods.

## Parameters

### stan_file (string, optional)
- Path to a `.stan` file containing Stan code
- Helper function `write_stan_file()` available for string-based program specification
- Required if `exe_file` is not provided

### exe_file (string, optional)
- Path to pre-compiled Stan executable
- Available with CmdStan 2.27+
- Can supplement or replace `stan_file`
- Note: if `stan_file` is omitted some `CmdStanModel` methods like code display and print functionality become unavailable

### compile (logical)
- Default: `TRUE`
- When `FALSE`, compilation deferred to later `$compile()` method call

### ... (additional arguments)
- Passed to `$compile()` method when `compile=TRUE`
- Options include executable directory specification, pedantic mode, include paths, C++ configuration

## Return Value

Returns a `CmdStanModel` object.

## Key Methods Available on Returned Object

- `$sample()` — MCMC sampling with parallel chain support
- `$optimize()` — Point estimation via LBFGS algorithm
- `$variational()` — ADVI posterior approximation
- `$laplace()` — Laplace approximation with optional Jacobian
- `$pathfinder()` — Alternative variational inference approach
- `$summary()` — Posterior summaries
- `$diagnostic_summary()` — Sampling diagnostics
- `$draws()` — Extract posterior samples
- `$print()` — Display Stan code with optional line numbers

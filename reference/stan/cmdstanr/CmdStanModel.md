# CmdStanModel Objects

## Overview

A `CmdStanModel` is an R6 class created by `cmdstan_model()` that manages Stan program files and their compiled executables, providing methods for model fitting using Stan's algorithms.

## Methods by Category

### Stan Code Management

- `$stan_file()` — Returns the file path to the Stan program
- `$code()` — Returns Stan program as a character vector
- `$print()` — Prints readable version of Stan program
- `$check_syntax()` — Validates Stan syntax without compilation
- `$format()` — Formats and canonicalizes Stan model code

### Compilation

- `$compile()` — Compiles Stan program
- `$exe_file()` — Returns compiled executable file path
- `$hpp_file()` — Returns `.hpp` file path with generated C++ code
- `$save_hpp_file()` — Saves the `.hpp` file
- `$expose_functions()` — Exposes Stan functions for R use

### Diagnostics

- `$diagnose()` — Runs gradient tests, returns `CmdStanDiagnose` object

### Model Fitting Methods

- `$sample()` — MCMC sampling, returns `CmdStanMCMC` object
- `$sample_mpi()` — MCMC with MPI parallelization, returns `CmdStanMCMC`
- `$optimize()` — Point estimation (LBFGS default), returns `CmdStanMLE`
- `$variational()` — ADVI approximation, returns `CmdStanVB`
- `$pathfinder()` — Pathfinder algorithm, returns `CmdStanPathfinder`
- `$generate_quantities()` — Generated quantities, returns `CmdStanGQ`

## Key Features

### Initial values specification supports:
- Functions returning parameter lists
- Functions accepting `chain_id` parameter
- Lists of lists for per-chain initialization

### Data specification:
- Named lists (RStan-style)
- File paths to JSON data files

### Output integration:
- Compatible with `posterior` package for summaries
- Works with `bayesplot` for visualization
- Supports `as_draws_df()` conversion

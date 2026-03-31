# Command-Line Interface Overview

## Overview

CmdStan executables use a command-line argument syntax consisting of keywords and keyword-value pairs. Arguments are organized by the following categories:

- **`method`** - specifies inference type (required)
- **`data`** - input data file specification
- **`output`** - program outputs configuration
- **`init`** - initial parameter values
- **`random`** - pseudo-random number seed

## Method Argument

The `method` argument is mandatory and can be specified as `method=<inference>` or implicitly as one of:

- `sample` - posterior sampling via HMC
- `optimize` - penalized maximum likelihood estimation
- `variational` - automatic variational inference
- `generate_quantities` - generate new quantities from existing sample
- `log_prob` - compute log probability and gradient
- `diagnose` - compare sampler gradients to finite differences

## Input Data Argument

Syntax: `data file=<filepath>`

The data file must be in JSON or Rdump format and contain definitions for all variables declared in the model's data block. Missing or mismatched variables cause program termination with an error message.

Example error:
"Exception: variable does not exist; processing stage=data initialization; variable name=y"

## Output Control Arguments

The `output` keyword accepts these sub-arguments:

- **`file=<filepath>`** - Stan CSV output file location (default: `output.csv`)
- **`diagnostic_file=<filepath>`** - auxiliary output file (default: none; valid for `sample` and `variational`)
- **`refresh=<int>`** - iterations between progress messages (default: 100)
- **`sig_figs=<int>`** - significant digits for numerical values, range 1-18 (default: 8)
- **`profile_file=<filepath>`** - profiling data output (default: `profile.csv`)
- **`save_cmdstan_config=<boolean>`** - save config to `<output>_config.json` (default: false)

## Initialize Model Parameters Argument

Parameters are initialized on the unconstrained scale. Default behavior: random draws from uniform distribution over [-2, 2].

The `init` argument accepts:

- **Positive real number *x*** - uniform distribution over [-*x*, *x*]
- **`0`** - zero initialization on unconstrained scale
- **Filepath** - JSON or Rdump file with initial values on constrained scale

Unspecified parameters use random initialization in [-2, 2].

## Random Number Generator Arguments

Syntax: `random seed=<int>`

If seed is unspecified or <= 0, system time generates a seed. The seed is recorded in output.

## Chain Identifier Argument

Syntax: `id=<int>` (default: 1)

Used with multiple chains to advance the random number generator, ensuring non-overlapping subsequences. When running multiple chains from the command line with a specified seed, set this to the chain index (1 through *n* chains).

For complete reproducibility, all environmental aspects must be controlled: OS, compilers, versions, Stan version, and all dependencies.

## Command Line Help

Display top-level help:

```
./bernoulli help
```

## Error Messages and Return Codes

CmdStan uses stdout for information and stderr for errors.

Return code meanings:

- **0** - Program terminated successfully
- **1-125** - Method could not run due to model/data issues
- **>128** - Fatal error during execution; subtract 128 to get signal number (e.g., 139 = signal 11, segmentation fault)

A return code of zero and no stderr output does not guarantee valid inference; diagnostic validation is still required.

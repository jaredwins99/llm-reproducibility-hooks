# Stan CSV File Format

## Overview

Stan outputs from all CmdStan methods use CSV format. "The output from all CmdStan methods is in CSV format. A Stan CSV file is a data table where the columns are the method and model parameters and quantities of interest."

Data values are numerical, including special representations: `NaN`, `inf`, `+inf`, `-inf`. Default precision is 8 digits, controllable via `sig_figs=<int>` argument.

Files include header rows and extensive comment lines beginning with `#`.

## CSV Column Names and Order

Columns are organized as: method-specific columns -> parameter block variables -> transformed parameters -> generated quantities (all in declaration order).

### Indexing Notation

- Variable name followed by element indices
- Indices delimited by periods ('.')
- 1-based indexing
- Tuples delimited by colons (':')

### Serialization Order

Container variables use column-major (Fortran) order. For a 3-D array with dimensions 2, 3, 4:

```
array[2, 3, 4] real foo;
```

First 6 columns labeled:
```
foo.1.1.1,foo.2.1.1,foo.1.2.1,foo.2.2.1,foo.1.3.1,foo.2.3.1
```

For tuples:
```
tuple(real, array[3] real) bar;
```

Columns labeled:
```
bar:1,bar:2.1,bar:2.2,bar:2.3
```

## MCMC Sampler CSV Output

Command example:
```
./bernoulli sample save_warmup=1 num_warmup=200 num_samples=100 \
            data file=bernoulli.data.json \
            output file=bernoulli_samples.csv
```

### Structure Components

**Initial comment rows** list configuration arguments indented hierarchically, with defaults annotated "(Default)".

**Header row** lists sampler parameters, model parameters, transformed parameters, and quantities of interest.

Example with single parameter:
```
lp__,accept_stat__,stepsize__,treedepth__,n_leapfrog__,divergent__,energy__,theta
```

Example with vector parameter (N=8):
```
mu,theta.1,theta.2,theta.3,theta.4,theta.5,theta.6,theta.7,theta.8,tau
```

**Warmup data rows** included when `save_warmup=1`.

Example values:
```
-6.74827,1,1,1,1,0,6.75348,0.247195
-6.74827,4.1311e-103,14.3855,1,1,0,6.95087,0.247195
```

**Adaptation comments** appear after warmup:
```
# Adaptation terminated
# Step size = 0.813694
# Diagonal elements of inverse mass matrix:
# 0.592879
```

For dense metric (e.g., eight schools):
```
# Adaptation terminated
# Step size = 0.211252
# Elements of inverse mass matrix:
# 25.6389, 17.3379, 13.9455, 15.9036, 15.1953, 8.73729, 16.9486, 14.4231, 17.4969, 0.518757
[...additional rows...]
```

**Sampling data rows** contain thinned draws.

Example:
```
-8.76921,0.796814,0.813694,1,1,0,9.75854,0.535093
-6.79143,0.979604,0.813694,1,3,0,9.13092,0.214431
```

**Timing information** at completion:
```
#  Elapsed Time: 0.005 seconds (Warm-up)
#                0.002 seconds (Sampling)
#                0.007 seconds (Total)
```

### Diagnostic CSV Output File

Contains configuration comments, header row, warmup draws (if `save_warmup=1`), sampling draws, and timing.

Columns include sampler parameters, model parameter estimates (unconstrained scale), latent Hamiltonian values, and gradients.

Labels use prefix `p_` for Hamiltonian columns and `g_` for gradient columns.

Example headers:
```
lp__,accept_stat__,stepsize__,treedepth__,n_leapfrog__,divergent__,energy__,theta,p_theta,g_theta
```

### Profiling CSV Output File

Plain CSV format with no metadata comments.

**Columns:**
- `name`: Profile statement name
- `thread_id`: Thread executing the statement
- `total_time`: Combined execution time
- `forward_time`: Forward pass time (or non-AD calculation)
- `reverse_time`: Reverse pass time
- `chain_stack`: Objects on chaining AD stack
- `no_chain_stack`: Objects on non-chaining AD stack
- `autodiff_calls`: Times executed with automatic differentiation
- `no_autodiff_calls`: Times executed without AD

## Optimization Output

Contains config comments, header row, and penalized maximum likelihood estimate.

## Variational Inference Output

Includes config comments, header row, adaptation comments, variational estimate, and sample draws from posterior estimate.

## Generate Quantities Outputs

Contains header row and quantities of interest.

## Diagnose Method Outputs

Contains header row and gradients.

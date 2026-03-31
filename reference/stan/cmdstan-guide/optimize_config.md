# CmdStan Optimization Guide

## Overview

The CmdStan executable runs optimization algorithms to find the posterior mode deterministically. Without convexity guarantees, the algorithm may locate local rather than global optima.

## Basic Usage

The minimal command structure:

```
./bernoulli optimize data file=bernoulli.data.json
```

The executable requires no recompilation when switching from sampling to optimization, and accepts identical data formats.

## Configuration Options

Access complete configuration via:
```
optimize help-all
```

All arguments and defaults display at execution start and in output CSV file comments.

## Output Format

Output streams to both console and CSV file. The default output filename is `output.csv`.

### Console Output Structure

First section displays configuration settings. Second section shows convergence results including:
- Iteration count
- Log probability value
- Parameter change magnitude (`||dx||`)
- Gradient magnitude (`||grad||`)
- Step size (`alpha`)
- Gradient evaluation count

Example output:
```
Initial log joint probability = -6.85653
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals
       5      -5.00402    0.00184936   3.35074e-05           1           1        8
Optimization terminated normally:
  Convergence detected: relative gradient magnitude is below tolerance
```

### CSV Output

Follows sampling pattern with configuration as comment lines, followed by headers and values:

```
lp__,theta
-5.00402,0.200003
```

The `lp__` field contains unnormalized log probability; remaining fields show parameter values.

## Jacobian Adjustments

### Purpose

For constrained parameters, Stan transforms to unconstrained space before optimization.

### Configuration

The `jacobian` argument determines whether log absolute Jacobian determinant of inverse parameter transforms receives inclusion:

**Without adjustment (default):**
- Returns modes in constrained parameter space
- Useful for finding original-space optima

**With adjustment:**
- Returns modes in unconstrained space
- Required for distributional approximations like Laplace sampling

## Optimization Algorithms

The `algorithm` argument accepts three values:

### LBFGS
- Quasi-Newton optimizer
- **Default selection**
- Significantly faster than alternatives
- Efficiently approximates Hessian information

### BFGS
- Quasi-Newton optimizer
- Slower than L-BFGS
- Full Hessian approximation

### Newton
- Newton optimizer
- Least efficient algorithm
- Auto-selects stepsize
- Calculates Hessian via finite differences
- **Not recommended**

## Iteration Saving

The `save_iterations` argument controls intermediate iteration storage:

**Default behavior (`false`):**
- Intermediate iterations display on console
- Final iteration only saved to output file

**When set to `true`:**
- All iterations (including initial) written to CSV file

Example command:
```
./bernoulli optimize save_iterations=1 data file=bernoulli.data.json
```

Example output with all iterations:
```
lp__,theta
-6.85653,0.493689
-6.10128,0.420936
-5.02953,0.22956
-5.00517,0.206107
-5.00403,0.200299
-5.00402,0.200003
```

## Quasi-Newton Configuration (BFGS/L-BFGS)

Convergence monitoring uses multiple tolerance values; satisfying any one terminates the algorithm.

### Shared Parameters

**`init_alpha`**
- Initial step size parameter
- Must be positive real number
- Default: 0.001
- Guidance: Set approximately equal to first-iteration alpha if initial iteration requires excessive function evaluations

**`tol_obj`**
- Convergence tolerance on objective function changes
- Must be positive real number
- Default: 1e-12

**`tol_rel_obj`**
- Convergence tolerance on relative objective function changes
- Must be positive real number
- Default: 10000

**`tol_grad`**
- Convergence tolerance on gradient norm
- Must be positive real number
- Default: 1e-08

**`tol_rel_grad`**
- Convergence tolerance on relative gradient norm
- Must be positive real number
- Default: 1e+07

**`tol_param`**
- Convergence tolerance on parameter value changes
- Must be positive real number
- Default: 1e-08

### L-BFGS Specific

**`history_size`**
- Hessian approximation history size
- Should remain below parameter dimensionality
- Typically 5-10 values suffice
- Default: 5
- Guidance: Increase if L-BFGS performs poorly while BFGS performs well; increases memory usage

## Newton Optimizer

No configuration parameters available. Finite difference Hessian computation causes slow performance.

---

## Default Configuration Output Example

```
method = optimize
  optimize
    algorithm = lbfgs (Default)
      lbfgs
        init_alpha = 0.001 (Default)
        tol_obj = 1e-12 (Default)
        tol_rel_obj = 10000 (Default)
        tol_grad = 1e-08 (Default)
        tol_rel_grad = 1e+07 (Default)
        tol_param = 1e-08 (Default)
        history_size = 5 (Default)
    jacobian = false (Default)
    iter = 2000 (Default)
    save_iterations = false (Default)
id = 1 (Default)
data
  file = bernoulli.data.json
init = 2 (Default)
random
  seed = 87122538 (Default)
output
  file = output.csv (Default)
  diagnostic_file =  (Default)
  refresh = 100 (Default)
  sig_figs = 8 (Default)
  profile_file = profile.csv (Default)
  save_cmdstan_config = false (Default)
num_threads = 1 (Default)
```

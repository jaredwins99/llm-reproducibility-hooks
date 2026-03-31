# Pathfinder Method for Approximate Bayesian Inference

## Overview

The CmdStan `pathfinder` method implements the Pathfinder algorithm from Zhang et al. (2022), which "generates a set of approximate draws" by running "multiple Pathfinder instances and using Pareto-smoothed importance resampling (PSIS)." The multi-path approach helps with non-normal densities and eliminates minor modes.

## Basic Usage

```
./bernoulli pathfinder data file=bernoulli.data.R
```

## Configuration Options

### Pathfinder Configuration

- **`num_psis_draws`**: Final number of draws from multi-path pathfinder. Positive integer, default: 1000
- **`num_paths`**: Number of single pathfinders. Positive integer, default: 4
- **`save_single_paths`**: Save outputs from individual pathfinders. Boolean, default: false
- **`max_lbfgs_iters`**: Maximum L-BFGS iterations. Positive integer, default: 1000
- **`num_draws`**: Approximate posterior draws per single pathfinder. Positive integer, default: 1000
- **`num_elbo_draws`**: Monte Carlo draws to evaluate ELBO. Positive integer, default: 25
- **`psis_resample`**: Perform PSIS resampling on draws. Boolean, default: true
- **`calculate_lp`**: Calculate log probabilities of approximate draws. Boolean, default: true

### L-BFGS Configuration

Arguments `init_alpha` through `history_size` control the L-BFGS optimizer with same defaults as optimization method.

## Output Files

### Default Output Structure

- `output.csv` - PSIS resampled draws (multi-path default)
- Columns: `lp_approx__`, `lp__`, model parameters, transformed parameters, generated quantities

### With `save_single_paths=true`

For 4 paths:
```
output.csv
output_path_1.csv
output_path_1.json
output_path_2.csv
output_path_2.json
output_path_3.csv
output_path_3.json
output_path_4.csv
output_path_4.json
```

## Example Output

```
method = pathfinder
  pathfinder
    init_alpha = 0.001 (Default)
    tol_obj = 1e-12 (Default)
    tol_rel_obj = 10000 (Default)
    tol_grad = 1e-08 (Default)
    tol_rel_grad = 1e+07 (Default)
    tol_param = 1e-08 (Default)
    history_size = 5 (Default)
    num_psis_draws = 1000 (Default)
    num_paths = 4 (Default)
    save_single_paths = false (Default)
    psis_resample = true (Default)
    calculate_lp = true (Default)
    max_lbfgs_iters = 1000 (Default)
    num_draws = 1000 (Default)
    num_elbo_draws = 25 (Default)
```

## Single-Path Pathfinder

Setting `num_paths=1` runs one pathfinder without PSIS reweighting. With `num_paths=1 save_single_paths=true`, the output includes the CSV sample and JSON ELBO iterations file.

## Reference

Zhang, Lu, Bob Carpenter, Andrew Gelman, and Aki Vehtari. 2022. "Pathfinder: Parallel Quasi-Newton Variational Inference." *Journal of Machine Learning Research* 23 (306): 1-49.

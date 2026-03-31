# Laplace Sampling Configuration

## Overview

The `laplace` method generates samples from a normal approximation centered at the mode of a distribution in unconstrained space. When the mode represents a maximum a posteriori (MAP) estimate, samples provide posterior mean and standard deviation estimates. For maximum likelihood estimates (MLE), samples estimate standard errors.

Key limitation: "the posterior mode in the unconstrained space doesn't correspond to the mean (nor mode) in the constrained space, and thus the sample is needed to infer the mean as well as the standard deviation."

This approach offers computational efficiency compared to exact Bayesian inference via MCMC, with accuracy dependent on mode estimation quality and Gaussian resemblance of the true posterior.

## Configuration Arguments

### mode
- **Purpose**: Input file containing parameter values on the constrained scale
- **Usage**: Typically generated from Stan's `optimize` method
- **Important**: When `optimize` uses default settings (jacobian=false), use `jacobian=false` in laplace. When `optimize` uses `jacobian=true`, use laplace's default `jacobian=true`.

### jacobian
- **Type**: Boolean
- **Default**: `true` (include adjustment)
- **Purpose**: Controls whether Jacobian adjustment is included in gradient calculation
- **Note**: Differs from optimization default (false) for historical reasons

### draws
- **Type**: Numeric
- **Default**: 1000
- **Purpose**: Total number of draws to return

### calculate_lp
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Controls log probability calculation at each draw
- **Output effect**: If false, `log_p__` column contains `nan` values

## CSV Output Format

Output files contain:

1. **Header section**: Full configuration options as CSV comments
2. **Column: log_p__**: Unnormalized log density
3. **Column: log_q__**: Unnormalized Laplace approximation density
4. **Parameter columns**: All model parameters on constrained scale

The `log_p__` and `log_q__` columns enable diagnostics and importance sampling applications.

## Diagnostic File Outputs

When requested via `output diagnostic_file=`, generates a JSON file containing:
- Log density evaluated at mode
- Gradient evaluated at mode
- Hessian of log density evaluated at mode

## Example Workflow

### Step 1: Obtain MAP Estimate
```
./examples/bernoulli/bernoulli optimize jacobian=1 \
  data file=examples/bernoulli/bernoulli.data.json \
  output file=bernoulli_optimize_lbfgs.csv random seed=1234
```

### Step 2: Run Laplace Sampling
```
./examples/bernoulli/bernoulli laplace mode=bernoulli_optimize_lbfgs.csv \
 data file=examples/bernoulli/bernoulli.data.json random seed=1234
```

### Example Output Header
```
# method = laplace
#   laplace
#     mode = bernoulli_lbfgs.csv
#     jacobian = true (Default)
#     draws = 1000 (Default)
#     calculate_lp = true (default)
# id = 1 (Default)
# data
#   file = examples/bernoulli/bernoulli.data.json
# init = 2 (Default)
# random
#   seed = 875960551 (Default)
# output
#   file = output.csv (Default)
#   diagnostic_file =  (Default)
#   refresh = 100 (Default)
#   sig_figs = 8 (Default)
#   profile_file = profile.csv (Default)
# num_threads = 1 (Default)
log_p__,log_q__,theta
-9.4562,-2.33997,0.0498545
-6.9144,-0.0117349,0.182898
-7.18171,-0.746034,0.376428
```

### Example Results
Bernoulli model results: mean 2.7, standard deviation 0.12 (compared to NUTS-HMC: mean 2.6, sd 0.12).

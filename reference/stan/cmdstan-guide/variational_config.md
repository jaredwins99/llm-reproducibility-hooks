# ADVI for Variational Inference

## Overview

Stan implements Automatic Differentiation Variational Inference (ADVI), described by Kucukelbir et al. (2017). The algorithm uses Monte Carlo integration to approximate the ELBO (evidence lower bound) and optimizes using stochastic gradient ascent in real-coordinate space.

## Algorithm Structure

The process consists of two phases:

1. **Adaptation Phase**: Finds optimal step size scaling parameter `eta`
2. **Sampling Phase**: Performs stochastic gradient ascent until convergence

"The algorithm runs until the mean change in ELBO drops below the specified tolerance."

## Basic Command

```
./bernoulli variational data file=bernoulli.data.R
```

## Variational Algorithms

Two algorithms are available, specified via the `algorithm` parameter:

- **`algorithm=meanfield`** (default): Uses fully factorized Gaussian approximation
- **`algorithm=fullrank`**: Uses Gaussian with full-rank covariance matrix

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `iter` | int | 10000 | Maximum iterations (must be > 0) |
| `grad_samples` | int | 1 | Monte Carlo samples for gradient estimation (> 0) |
| `elbo_samples` | int | 100 | Monte Carlo samples for ELBO estimation (> 0) |
| `eta` | double | 1.0 | Stepsize weighting parameter (> 0) |
| `tol_rel_obj` | double | 0.01 | Convergence tolerance on relative norm (> 0) |
| `eval_elbo` | int | 100 | Evaluate ELBO every Nth iteration (> 0) |
| `output_samples` | int | 1000 | Posterior samples to draw and save (> 0) |

### Adaptation Sub-options

- `adapt_engaged`: Boolean, default `true`
- `adapt_iter`: Integer, default `50` (must be > 0)

## CSV Output Structure

The output file contains:

1. Configuration metadata as CSV comments
2. Column headers: `lp__`, `log_p__`, `log_g__`, then model parameters
3. Stepsize adaptation information as comments
4. Mean of variational approximation (first data row)
5. `output_samples` number of draws from the approximation

Example output row:
```
0,-14.0252,-5.21718,0.770397
```

## Console Output Example

```
Begin eta adaptation.
Iteration:   1 / 250 [  0%]  (Adaptation)
...
Success! Found best value [eta = 1] earlier than expected.

Begin stochastic gradient ascent.
  iter             ELBO   delta_ELBO_mean   delta_ELBO_med   notes
   100           -6.131             1.000            1.000
  1500           -6.241             0.015            0.010   MEDIAN ELBO CONVERGED

Drawing a sample of size 1000 from the approximate posterior...
COMPLETED.
```

## Key Characteristics

- The algorithm is "stochastic, which makes it challenging to assess convergence"
- ELBO values are Monte Carlo estimates, introducing variability
- Convergence assessed via relative tolerance on objective function
- Default output file: `output.csv`
- Supports `variational help-all` subcommand for complete configuration options

# Diagnostic Mode - Stan Reference Manual

## Overview

Stan's diagnostic mode evaluates a probabilistic program by computing the log probability and its gradients, then comparing the program's gradient calculations against finite difference approximations. This helps verify the correctness of gradient computations in Stan models.

## Configuration Parameters

Two parameters control diagnostic mode behavior:

| Parameter | Description | Constraints | Default |
|-----------|-------------|-------------|---------|
| `epsilon` | Finite difference step size | (0, inf) | 1e-6 |
| `error` | Error threshold for gradient matching | (0, inf) | 1e-6 |

If computed gradients deviate from finite difference estimates beyond the specified threshold, the relevant parameter is flagged.

## Output Information

The diagnostic mode produces:

- **Log posterior density** (up to proportionality) at specified initial values
- **Gradient values** for each parameter, calculated both by Stan's automatic differentiation and by finite differences
- **Unconstrained scale representation** where each variable corresponds to its number of unconstrained parameters (e.g., an N x N correlation matrix requires C(N,2) unconstrained parameters)
- **Jacobian adjustment** included in log density calculations based on declared constraints

## Configuration and Initialization

Configuration options match those for MCMC sampling. Initial parameter values can be user-specified or randomly generated. Random number generator settings only affect randomized initialization.

## Performance Considerations

"Due to the application of finite differences, the computation time grows linearly with the number of parameters." This becomes problematic for models with latent parameters scaling with data size. Using smaller datasets during model diagnosis can significantly reduce computation time.

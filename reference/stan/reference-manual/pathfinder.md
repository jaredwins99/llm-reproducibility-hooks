# Pathfinder Algorithm in Stan

## Overview

The Pathfinder algorithm is a variational inference method implemented in Stan that "locates normal approximations to the target density along a quasi-Newton optimization path, with local covariance estimated using the negative inverse Hessian estimates produced by the LBFGS optimizer."

Stan offers two implementations:

1. **Single-path Pathfinder**: Generates approximate draws from one algorithmic run
2. **Multi-path Pathfinder**: Uses importance resampling across multiple runs to better handle non-normal densities and mitigate local optima issues

## Performance Characteristics

Compared to ADVI and short dynamic HMC runs, Pathfinder demonstrates substantially improved efficiency, requiring "one to two orders of magnitude fewer log density and gradient evaluations."

## Diagnostic Approach

Pathfinder evaluates approximation quality through the Pareto-k-hat diagnostic, which assesses whether density ratios can enhance the approximation via resampling. Interpretation guidelines:

- **k-hat < 0.7**: Resampled draws are nearly equivalent to posterior samples for initializing MCMC
- **k-hat > 0.7**: Draws lack reliability for direct inference but remain superior to arbitrary random initialization

When k-hat exceeds 0.7, importance resampling without replacement is recommended to ensure unique chain initializations.

## References

The methodology originates from Zhang et al. (2022) and employs diagnostics from Vehtari et al. (2024).

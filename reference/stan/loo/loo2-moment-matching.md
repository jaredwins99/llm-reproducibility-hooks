# Avoiding Model Refits in Leave-One-Out Cross-Validation with Moment Matching

Source: https://mc-stan.org/loo/articles/loo2-moment-matching.html

Vignette from the loo package (version 2.9.0) demonstrating how to improve LOO-CV accuracy without repeatedly refitting models.

## Key Concepts

### Pareto k Diagnostics

The package automatically monitors sampling accuracy using Pareto k values for each observation. Values above 0.7 indicate problematic estimates where the model assessment becomes unreliable.

### Moment Matching Solution

Instead of refitting models via MCMC (computationally expensive), the method uses "additional computations using the existing posterior sample" to improve accuracy.

## The Roach Eradication Example

Uses a Poisson regression model for roach counts with an offset term. Initial `loo()` results showed 15 problematic observations (Pareto k > 0.7), requiring either 15 refits or an alternative approach.

## Results

When applying moment matching via `loo(fit, moment_match = TRUE)`:
- All Pareto k values improved to less than 0.7
- The `elpd_loo` estimate changed from -5457.8 to -5478.5, indicating the original estimate had overestimated predictive performance

## Important Distinction

The package maintains two sets of Pareto k values:
- **Updated values** (in `diagnostics$pareto_k`): Algorithmic indicators of sampling accuracy
- **Original values** (in `pointwise[,"influence_pareto_k"]`): Diagnostics showing each observation's influence on the posterior

## Implementation

Users can either:
- Use the direct approach with `loo(moment_match = TRUE)`
- Call `loo_moment_match()` with five helper functions for custom model implementations

# Using the loo Package (version >= 2.0.0)

Source: https://mc-stan.org/loo/articles/loo2-example.html

Vignette demonstrating the loo package (version 2.9.0) for Pareto smoothed importance-sampling leave-one-out cross-validation (PSIS-LOO).

## Overview

Demonstrates how to use loo for model checking and comparison. References foundational papers by Vehtari, Gelman, Gabry and others on practical Bayesian model evaluation and Pareto smoothed importance sampling.

## Setup

Required packages: rstanarm, bayesplot, and loo.

## Example: Roaches Dataset Analysis

Uses data from Gelman and Hill (2007) examining pest management efficacy. The dataset contains 262 observations with variables:
- y (roach count)
- roach1 (pre-treatment count)
- treatment indicator
- senior status
- exposure2 (trap days)

### Model Comparisons

**Poisson regression model (fit1)**:
- Showed poor diagnostics with 17 observations having Pareto k > 0.7
- p_loo approximately 292 (far exceeding the number of parameters)

**Negative binomial model (fit2)**:
- Improved substantially with only 1 problematic observation
- p_loo approximately 6.7

## Key Findings

- The Poisson model exhibited severe misspecification
- LOO-PIT checks revealed under-dispersion in the Poisson model
- The negative binomial model provided dramatically better predictive performance (ELPD difference of 5352)
- Model refitting for high k-values yielded MCSE of 0.1

## References

Gabry, Gelman, Hill, and Vehtari on Bayesian visualization, statistical modeling, and importance sampling methodologies.

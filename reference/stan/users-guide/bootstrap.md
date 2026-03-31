# The Bootstrap and Bagging

## Overview

The bootstrap is a Monte Carlo technique for approximating the error distribution of an estimator. As the documentation explains, "The bootstrap is a technique for approximately sampling from the error distribution for an estimator."

The method works by repeatedly resampling the original data with replacement and computing estimates from each subsample. This allows researchers to estimate standard errors and confidence intervals without making strong distributional assumptions.

Bagging (bootstrap aggregation) extends this approach by combining multiple bootstrapped models to produce more robust predictions and inferences.

## Core Concepts

**Estimators**: An estimator is simply a function mapping data to numerical estimates. Examples include the sample mean or maximum likelihood estimates. When data is treated as a random variable, the estimator becomes a random variable too, enabling analysis of its sampling properties.

**The Bootstrap Procedure**: The basic algorithm involves:
1. Resampling the original data with replacement M times
2. Computing the estimate from each resample
3. Using quantiles of these estimates for confidence intervals and standard errors

## Stan Implementation

The documentation provides a linear regression example where a `resample` parameter controls whether to use original or bootstrapped data. The key element is generating bootstrap indices:

```stan
simplex[N] uniform = rep_vector(1.0 / N, N);
array[N] int<lower=1, upper=N> boot_idxs;
for (n in 1:N) {
  boot_idxs[n] = resample ? categorical_rng(uniform) : n;
}
```

These indices allow the model to be fit to different subsamples by indexing into the data: `y[boot_idxs]` and `x[boot_idxs]`.

## Error Statistics

**Standard Errors**: Running the model multiple times across bootstrap samples produces Monte Carlo estimates of parameter uncertainty. "With a total of M = 100 bootstrap samples, there are 100 estimates of α, 100 of β, and 100 of σ."

**Confidence Intervals**: The 2.5% and 97.5% quantiles of bootstrap estimates provide 95% confidence interval boundaries. More samples are needed for accurate tail estimates than for standard errors.

## Bayesian Extensions

The bootstrap applies equally to Bayesian point estimates (posterior means or medians). Bagged posteriors tend to produce wider intervals than those from original data alone, reflecting guard against model misspecification rather than true Bayesian updating.

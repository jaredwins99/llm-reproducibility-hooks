# LOO Package Function Reference

Source: https://mc-stan.org/loo/reference/index.html

loo version 2.9.0 -- Efficient leave-one-out cross-validation (LOO-CV) and WAIC for Bayesian models. Led by Aki Vehtari and team.

## Datasets

Included datasets: Kline, milk, voice, and voice_loo

## Approximate LOO-CV Functions

- **`loo()`** -- Efficient approximate leave-one-out cross-validation (LOO)
- **`loo_subsample()`** -- LOO using subsampling for efficiency
- **`loo_approximate_posterior()`** -- LOO for posterior approximations
- **`loo_moment_match()`** and **`loo_moment_match_split()`** -- Moment matching approaches
- **`psis()`** -- Pareto smoothed importance sampling (PSIS)
- **`tis()`** -- Truncated importance sampling
- **`sis()`** -- Standard importance sampling
- Diagnostic functions for Pareto smoothing (pareto_k tables, plotting)

## Model Comparison & Weighting

- **`loo_compare()`** -- Model comparison functionality
- **`loo_model_weights()`** -- Model averaging via stacking or pseudo-BMA weighting

## K-fold Cross-Validation Helpers

- **`kfold_split_random()`**, **`kfold_split_stratified()`**, **`kfold_split_grouped()`**
- Generic **`kfold()`** function

## Additional Functions

- **`waic()`** -- Widely applicable information criterion
- **`crps()`** / **`scrps()`** -- Continuously ranked probability scores
- **`extract_log_lik()`** -- Extract log-likelihood from Stan models
- **`gpdfit()`** -- Generalized Pareto distribution parameter estimation

## Deprecated Functions

- `compare()` and `psislw()` (older versions)

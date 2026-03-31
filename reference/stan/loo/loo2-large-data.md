# Using Leave-one-out Cross-Validation for Large Data

Source: https://mc-stan.org/loo/articles/loo2-large-data.html

Vignette from the loo package (version 2.9.0) demonstrating LOO cross-validation methods for large datasets using Stan and R.

## Key Methods

### 1. LOO with Subsampling

The `loo_subsample()` function creates efficient PSIS-LOO approximations by taking a subsample (e.g., size 100) for computational efficiency while working with thousands of total observations.

The subsampling approach provides additional uncertainty quantification through "subsampling SE" columns in output, reflecting the extra variability from sampling observations.

### 2. LOO with Posterior Approximations

`loo_approximate_posterior()` works with Laplace approximations from Stan's `optimizing()` function. This method corrects for posterior approximation when computing expected log predictive density (elpd).

### 3. Combined Approach

Users can combine posterior approximation correction with subsampling for further computational gains.

## Practical Example

Uses well-water switching data from Bangladesh (N=3,020) with a logistic regression model. All Pareto k estimates remained good (k < 0.7) across methods, indicating reliable LOO approximations.

## Model Comparison

The `loo_compare()` function enables model comparison using identical subsampled observations to improve standard error estimates and capture correlations between models.

## References

Magnusson et al. (2020) and Vehtari et al. (2017, 2024).

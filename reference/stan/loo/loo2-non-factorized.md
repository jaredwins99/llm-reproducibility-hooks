# Leave-One-Out Cross-Validation for Non-Factorized Models

Source: https://mc-stan.org/loo/articles/loo2-non-factorized.html

By Aki Vehtari, Paul Burkner, and Jonah Gabry. Explains LOO-CV for Bayesian models with non-factorized observation models, particularly multivariate normal and Student-t models.

## Factorized vs. Non-Factorized Models

**Factorized models** express likelihoods as products of observation-specific components, allowing straightforward pointwise likelihood calculations.

**Non-factorized models** specify joint likelihoods without independent factorization, making direct LOO calculations impossible or inefficient.

## LOO-CV Methodology

For multivariate normal models with covariance matrix C, the LOO predictive quantities are based on Sundararajan and Keerthi (2001):

- LOO predictive mean: mu_y,-i = y_i - c_bar_ii^(-1) * g_i
- LOO predictive standard deviation: sigma_y,-i = sqrt(c_bar_ii^(-1))

## Two Computational Approaches

### 1. Approximate LOO-CV (PSIS-LOO)

Uses "integrated importance sampling" to approximate the integral over leave-one-out posteriors:
- Uses posterior draws from the full model
- Computes importance weights via Pareto Smoothed Importance Sampling (PSIS)
- Avoids expensive refitting
- Includes Pareto k diagnostics to assess approximation reliability

### 2. Exact LOO-CV with Refitting

For validation or problematic observations:
- Treats held-out observations as missing parameters
- Refits the model N times (computationally expensive)
- Computes conditional predictive distributions for each fold

## Case Study: Spatial SAR Models

Demonstrated using Columbus, Ohio neighborhood crime data with a lagged SAR (simultaneously autoregressive) model:

Formula: (I - rho*W)y = eta + epsilon

Where rho represents spatial correlation and W is a weight matrix capturing neighborhood adjacency.

### Implementation Details

- Custom Stan function `normal_lagsar_lpdf` for efficient SAR likelihood computation
- R code using **brms** to specify and fit the spatial model
- Step-by-step calculations for both approximate and exact LOO-CV

### Validation Results

Comparing approximate versus exact LOO-CV:
- Overall ELPD estimates: approximate = -186.8, exact = -187.9
- Strong correspondence except for flagged problematic observations
- Without the problematic fourth observation: -172.9 vs. -173.3

Discrepancies reflect "violations of PSIS-LOO assumptions" rather than implementation errors.

## References

Burkner, Gabry, and Vehtari (2020) in *Computational Statistics*, with supporting theory from Vehtari et al. (2016, 2017, 2024).

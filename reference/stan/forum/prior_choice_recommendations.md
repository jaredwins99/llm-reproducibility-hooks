# Prior Choice Recommendations

Sources:
- https://discourse.mc-stan.org/t/prior-choice-recommendations-wiki/11580
- https://discourse.mc-stan.org/t/suggestion-for-prior-choice-recommendations-wiki/11584

## GitHub Wiki

The canonical reference is the Prior Choice Recommendations wiki on the Stan GitHub
repository: https://github.com/stan-dev/stan/wiki/Prior-Choice-Recommendations

This wiki is maintained by Andrew Gelman and collaborators and is "always under
development as new ideas and new experiences come in."

## Key Recommendations

### Variability Parameters (Standard Deviations, Variances)

**Problematic approach**: Using peaked-at-zero priors (e.g., `normal(0,1)`) for
measurement error implies implausibly high confidence in perfect accuracy.

**Recommended alternatives**:
- **Weibull(2,1)**: Provides zero-avoiding properties
- **Gamma priors**: Avoid zero values in marginal posterior mode estimation
- **Wishart (not inverse-Wishart)**: Recommended for covariance matrices to prevent
  degenerate estimates

### Hierarchical Model Scale Parameters
- **half-normal(0,1)** or **half-t(4,0,1)** as sensible defaults
- Peaked-at-zero priors can be useful for shrinkage but inappropriate when zero is
  not plausible (e.g., measurement error)

### Regression Coefficients
- Default weakly informative: `normal(0, 2.5)` on standardized predictors
- Consider student_t for robustness
- QR reparameterization makes prior specification easier for correlated predictors

## Expert Insights

- Andrew Gelman: Zero-avoidance serves computational purposes by mitigating funnel
  behavior in posteriors. "Peaked-at-zero" characterization may be misleading on the
  log-scale where no peak exists at zero.
- Paul Burkner: Default priors in brms are often "too wide" -- prior specification
  is an area needing improvement.

## Practical Advice

1. Always visualize priors before model fitting
2. Check prior predictive distributions
3. Compare prior to posterior to ensure data is informative
4. Use domain knowledge to set reasonable bounds
5. Avoid improper or flat priors -- they cause computational problems

## Referenced Research

- Chung et al. on zero-avoiding priors for marginal posterior estimation
  (Columbia University)
- Gelman's recommendations on weakly informative priors (2006, updated)

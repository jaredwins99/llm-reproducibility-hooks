# Measurement Error and Meta-Analysis

## Overview

This Stan documentation page addresses two interconnected statistical challenges: handling measurement error in data and combining results across multiple studies through meta-analysis.

## Bayesian Measurement Error Models

The Bayesian approach treats true unmeasured quantities as missing data that can be estimated alongside other parameters. This is particularly valuable when measurement error is substantial relative to the quantities being measured.

### Regression with Measurement Error

The foundational linear regression model includes a predictor `x`, outcome `y`, with parameters for intercept (alpha), slope (beta), and outcome noise (sigma).

When true predictor values remain unknown but measurements are available, the framework introduces latent parameters for true values. The measurement model specifies: "measured_value ~ normal(true_value, measurement_noise)". True values receive hierarchical priors, allowing the model to estimate both regression coefficients and account for measurement uncertainty simultaneously.

Extensions include richer measurement error distributions and exposure models that regress unknown risk factors on known covariates.

### Rounding as Measurement Error

Rounding represents a common measurement error type. The documentation uses Exercise 3.5(b) from Gelman et al., involving five weight measurements rounded to the nearest pound: 10, 10, 12, 11, 9.

For unrounded measurement z_n and rounded observation y_n, the likelihood integrates the normal density over the rounding interval:

The probability becomes: Φ((y_n + 0.5 - μ)/σ) - Φ((y_n - 0.5 - μ)/σ)

Stan implementation uses either: (1) direct likelihood calculation via `log_diff_exp` function, or (2) latent parameters constrained within rounding intervals. The latent parameter approach provides approximately twice the efficiency in effective sample size per iteration.

## Meta-Analysis Framework

Meta-analysis pools data from multiple studies, treating each study's estimates as noisy measurements of underlying quantities of interest. This naturally fits Bayesian hierarchical modeling.

### Treatment Effects in Controlled Studies

The example involves J clinical trials, each providing binomial outcomes for treatment and control groups.

**Data Structure**: Each trial j contains:
- n_t[j]: treatment cases
- r_t[j]: successful treatment outcomes
- n_c[j]: control cases
- r_c[j]: successful control outcomes

**Transformation**: Raw binomial data converts to log odds ratios and standard errors:

y_j = log(r_t[j]/(n_t[j]-r_t[j])) - log(r_c[j]/(n_c[j]-r_c[j]))

σ_j = √(1/r_t[j] + 1/(n_t[j]-r_t[j]) + 1/r_c[j] + 1/(n_c[j]-r_c[j]))

**Fixed Effects Model**: Assumes a single global treatment effect parameter theta, with observed log odds normally distributed around this value with study-specific standard errors.

**Random Effects (Hierarchical) Model**: Allows per-trial treatment effects theta[j], estimated alongside hyperparameters for the mean effect (mu) and between-trial variation (tau). The hierarchical structure uses wide priors on mu and tau relative to data scale.

## Key References

- Clayton (1992): Models for cohort studies with inaccurately measured exposures
- Gelman et al. (2013): Comprehensive Bayesian Data Analysis text
- Rubin (1981): Hierarchical meta-analysis of SAT coaching across eight schools
- Warn, Thompson, and Spiegelhalter (2002): Binary outcome meta-analysis methods

The page emphasizes that Bayesian frameworks excel at meta-analysis because previous studies naturally embed within measurement error models of underlying parameters of interest.

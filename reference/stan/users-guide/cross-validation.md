# Held-Out Evaluation and Cross-Validation

## Overview

The document describes two core evaluation strategies for Bayesian models built with Stan:

**Held-out evaluation** involves splitting data into training and test sets. The training portion estimates model parameters, while the test portion assesses predictive performance.

**Cross-validation** extends this approach by creating multiple train/test splits. "Leave-one-out (LOO) cross-validation" represents the extreme case where each observation serves as the test set individually.

## Key Sections

### Posterior Predictive Density Evaluation

The posterior predictive density formula integrates over parameter uncertainty:

p(ỹ | x̃, x, y) = ∫ p(ỹ | x̃, θ) · p(θ | x, y) dθ

This is approximated using Monte Carlo sampling across posterior draws. To prevent computational underflow, calculations use log-scale transformations with the log-sum-exp function.

### Stan Implementation Example

A linear regression model demonstrates computing log predictive density for test observations:

```stan
data {
  int<lower=0> N;
  vector[N] y;
  vector[N] x;
  int<lower=0> N_tilde;
  vector[N_tilde] x_tilde;
  vector[N_tilde] y_tilde;
}
parameters {
  real alpha;
  real beta;
  real<lower=0> sigma;
}
model {
  y ~ normal(alpha + beta * x, sigma);
}
generated quantities {
  real log_p = normal_lpdf(y_tilde | alpha + beta * x_tilde, sigma);
}
```

### Error Metrics

**Squared error** and **absolute error** quantify estimation accuracy:
- Squared error: (θ̂ - θ)²
- Absolute error: |θ̂ - θ|

For multiple outcomes, **mean square error (MSE)** and **root mean square error (RMSE)** summarize performance across observations.

### Cross-Validation Implementation

The document provides a Stan function for random permutations:

```stan
functions {
  array[] int permutation_rng(int N) {
    array[N] int y;
    for (n in 1 : N) {
      y[n] = n;
    }
    vector[N] theta = rep_vector(1.0 / N, N);
    for (n in 1 : size(y)) {
      int i = categorical_rng(theta);
      int temp = y[n];
      y[n] = y[i];
      y[i] = temp;
    }
    return y;
  }
}
```

### Important Considerations

**Structured data** requires careful cross-validation. "One needs to cross-validate at the document level, not at the individual word level" when data groups naturally by document or other clusters.

**Spatio-temporal data** demands context-specific approaches. Predictions may target future weeks given historical data, requiring different evaluation strategies than random splits.

The document references **approximate cross-validation** methods (Vehtari et al. 2017), implemented in the R package `loo`, which approximates leave-one-out evaluation from a single model fit.

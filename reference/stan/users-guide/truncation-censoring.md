# Truncated or Censored Data

## Overview

This Stan documentation section explains how to model data with truncation or censoring. "Data in which measurements have been truncated or censored can be coded in Stan following their respective probability models."

## Truncated Distributions

Truncation in Stan applies only to univariate distributions where log CDF and log complementary CDF functions exist. The reference manual provides detailed information on these mathematical functions.

## Truncated Data

Truncated data represents measurements reported only within specific bounds. For example, data above a lower limit, below an upper limit, or within a range.

### Example Model

A right-truncated normal model:

```stan
data {
  int<lower=0> N;
  real U;
  array[N] real<upper=U> y;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  y ~ normal(mu, sigma) T[ , U];
}
```

The model declares an upper bound as data and constrains observations accordingly.

### Constraints and Out-of-Bounds Returns

Values outside truncation ranges produce zero probability (log probability = −∞). Parameters should be constrained appropriately:

```stan
parameters {
  array[N] real<lower=L, upper=U> y;
}
```

For unknown bounds that are parameters:

```stan
parameters {
  real<upper=min(y)> L;
  real<lower=fmax(L, max(y))> U;
}
```

### Unknown Truncation Points

When truncation points are estimated as parameters:

```stan
data {
  int<lower=1> N;
  array[N] real y;
}
parameters {
  real<upper=min(y)> L;
  real<lower=max(y)> U;
  real mu;
  real<lower=0> sigma;
}
model {
  L ~ // prior specification
  U ~ // prior specification
  y ~ normal(mu, sigma) T[L, U];
}
```

Informative priors are essential to prevent concentration around data extremes.

## Censored Data

Censoring masks values beyond thresholds, but the count of censored observations is known. A household scale not reporting weights above 300 pounds exemplifies this scenario.

### Estimating Censored Values

Censored data can be treated as constrained missing values:

```stan
data {
  int<lower=0> N_obs;
  int<lower=0> N_cens;
  array[N_obs] real y_obs;
  real<lower=max(y_obs)> U;
}
parameters {
  array[N_cens] real<lower=U> y_cens;
  real mu;
  real<lower=0> sigma;
}
model {
  y_obs ~ normal(mu, sigma);
  y_cens ~ normal(mu, sigma);
}
```

Censored values are sampled as parameters constrained above the threshold.

### Integrating Out Censored Values

Rather than imputing censored values, integrate them analytically. The probability that censored observations exceed U is:

**P[y_cens,m > U] = 1 − Φ((U − μ)/σ)**

The log-likelihood for M censored observations becomes:

**log ∏(m=1 to M) P[y_cens,m > U] = M × normal_lccdf(U | μ, σ)**

Implementation:

```stan
data {
  int<lower=0> N_obs;
  int<lower=0> N_cens;
  array[N_obs] real y_obs;
  real<lower=max(y_obs)> U;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  y_obs ~ normal(mu, sigma);
  target += N_cens * normal_lccdf(U | mu, sigma);
}
```

For left-censored data, use `normal_lcdf` instead. When the censoring threshold is unknown, move it from data to parameters block.

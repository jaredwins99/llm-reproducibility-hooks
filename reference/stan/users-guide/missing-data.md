# Missing Data and Partially Known Parameters

## Overview

Bayesian inference treats missing data as unknown parameters to be estimated in the posterior distribution. Stan requires observed and unknown quantities in separate program blocks, necessitating code to combine observed and missing data structures.

## Missing Data

Stan distinguishes between known quantities (declared in `data` and `transformed data` blocks) and unknown quantities (declared in `parameters` block).

### Example: Missing Normal Observations

```stan
data {
  int<lower=0> N_obs;
  int<lower=0> N_mis;
  array[N_obs] real y_obs;
}
parameters {
  real mu;
  real<lower=0> sigma;
  array[N_mis] real y_mis;
}
model {
  y_obs ~ normal(mu, sigma);
  y_mis ~ normal(mu, sigma);
}
```

The observed data points are provided as `y_obs`, while missing values are declared as parameter array `y_mis`. Both are modeled under the same distribution with location `mu` and scale `sigma`.

## Partially Known Parameters

When multivariate probability functions have partially observed outcomes or parameters, you can create vectors mixing known and unknown values in the `transformed parameters` block.

### Example: Bivariate Covariance Matrix with Known Variances

```stan
data {
  int<lower=0> N;
  array[N] vector[2] y;
  real<lower=0> var1;
  real<lower=0> var2;
}
transformed data {
  real<lower=0> max_cov = sqrt(var1 * var2);
  real<upper=0> min_cov = -max_cov;
}
parameters {
  vector[2] mu;
  real<lower=min_cov, upper=max_cov> cov;
}
transformed parameters {
  matrix[2, 2] Sigma;
  Sigma[1, 1] = var1;
  Sigma[1, 2] = cov;
  Sigma[2, 1] = cov;
  Sigma[2, 2] = var2;
}
model {
  y ~ multi_normal(mu, Sigma);
}
```

Variances are fixed as data while covariance is estimated as a parameter. The constraint ensures positive definiteness of the covariance matrix.

## Sliced Missing Data

For missing data within larger structures, index arrays and slicing effectively reassemble data.

### Example: Time-Series with Partial Observations

```stan
data {
  int<lower=0> N_obs;
  int<lower=0> N_mis;
  array[N_obs] int<lower=1, upper=N_obs + N_mis> ii_obs;
  array[N_mis] int<lower=1, upper=N_obs + N_mis> ii_mis;
  array[N_obs] real y_obs;
}
transformed data {
  int<lower=0> N = N_obs + N_mis;
}
parameters {
  array[N_mis] real y_mis;
  real<lower=0> sigma;
}
transformed parameters {
  array[N] real y;
  y[ii_obs] = y_obs;
  y[ii_mis] = y_mis;
}
model {
  sigma ~ gamma(1, 1);
  y[1] ~ normal(0, 100);
  y[2:N] ~ normal(y[1:(N - 1)], sigma);
}
```

Index arrays identify positions of observed and missing data in the complete time series.

## Loading Matrix for Factor Analysis

For Bayesian factor analysis, construct a Cholesky factor with unit diagonal by declaring below-diagonal elements as parameters.

```stan
data {
  int<lower=2> K;
}
transformed data {
  int<lower=1> K_choose_2;
  K_choose_2 = (K * (K - 1)) / 2;
}
parameters {
  vector[K_choose_2] L_lower;
}
transformed parameters {
  cholesky_factor_cov[K] L;
  for (k in 1:K) {
    L[k, k] = 1;
  }
  {
    int i;
    for (m in 2:K) {
      for (n in 1:(m - 1)) {
        L[m, n] = L_lower[i];
        L[n, m] = 0;
        i += 1;
      }
    }
  }
}
```

Place priors directly on `L_lower` rather than the full covariance matrix to avoid Jacobian adjustments.

## Missing Multivariate Data

When some components of multivariate outcomes are missing, model using marginal distributions for unobserved components.

### Example: Bivariate Missing Data

```stan
array[N] vector[2] y;
array[N, 2] int<lower=0, upper=1> y_observed;
```

Use conditional logic to apply appropriate distributions:

```stan
for (n in 1:N) {
  if (y_observed[n, 1] && y_observed[n, 2]) {
    y[n] ~ multi_normal(mu, Sigma);
  } else if (y_observed[n, 1]) {
    y[n, 1] ~ normal(mu[1], sqrt(Sigma[1, 1]));
  } else if (y_observed[n, 2]) {
    y[n, 2] ~ normal(mu[2], sqrt(Sigma[2, 2]));
  }
}
```

For efficiency, vectorize by constructing index arrays in `transformed data`:

```stan
transformed data {
  array[observed_12(y_observed)] int ns12;
  array[observed_1(y_observed)] int ns1;
  array[observed_2(y_observed)] int ns2;
}
```

Then vectorize probability statements:

```stan
y[ns12] ~ multi_normal(mu, Sigma);
y[ns1] ~ normal(mu[1], sqrt(Sigma[1, 1]));
y[ns2] ~ normal(mu[2], sqrt(Sigma[2, 2]));
```

This approach is more efficient than latent variable imputation when marginalizing analytically is feasible.

# QR Decomposition for Regression Models

**Michael Betancourt** | July 2017

Source: https://mc-stan.org/learn-stan/case-studies/qr_regression.html

---

## Overview

A common problem in regression modeling is correlation amongst the covariates which can induce strong posterior correlations that complicate accurate computation in Bayesian inference. This case study demonstrates how QR decomposition addresses this challenge.

## Problem Demonstration

The author begins with a simple two-covariate example where X follows a normal distribution and X^2 is included. The correlations here are particularly strong because the covariate was not standardized before transformation. Powers are much better identified when the input is centered around zero.

### R Data Generation

```r
set.seed(689934)

N <- 5000
x <- rnorm(N, 10, 1)
X = t(data.matrix(data.frame(x, x * x)))

M <- 2
beta = matrix(c(2.5, -1), nrow=M, ncol=1)
alpha <- -0.275
sigma <- 0.8

mu <- t(X) %*% beta + alpha
y = sapply(1:N, function(n) rnorm(1, mu[n], sigma))

stan_rdump(c("N", "M", "X", "y"), file="regr.data.R")
```

## Naive Regression Model

```stan
data {
  int<lower=1> N;
  int<lower=1> M;
  matrix[M, N] X;
  vector[N] y;
}

parameters {
  vector[M] beta;
  real alpha;
  real<lower=0> sigma;
}

model {
  beta ~ normal(0, 10);
  alpha ~ normal(0, 10);
  sigma ~ cauchy(0, 10);

  y ~ normal(X' * beta + alpha, sigma);
}
```

### Fitting

```r
input_data <- read_rdump("regr.data.R")
fit <- stan(file='regr.stan', data=input_data, seed=483892929)
```

The naive model exhibits 12 saturated tree-depth iterations (0.3% of 4000 total), suggesting sampling difficulty due to posterior correlations between the correlated covariates.

## The QR Decomposition Solution

Rather than fitting the model directly on correlated covariates, the technique decorrelates them through orthogonalization.

### Mathematical Foundation

The QR decomposition expresses the design matrix as:

    X = Q * R

where Q contains orthonormal columns (Q'Q = I) and R is upper triangular. This decomposition enables reparameterization that reduces posterior correlation structure.

Given the regression model:

    y ~ Normal(X * beta + alpha, sigma)

We can substitute X = Q * R to get:

    y ~ Normal(Q * R * beta + alpha, sigma)
    y ~ Normal(Q * theta + alpha, sigma)

where theta = R * beta. Because Q has orthonormal columns, the parameters theta are decorrelated. After fitting, we recover the original parameters via:

    beta = R^{-1} * theta

### QR Regression Model in Stan

The QR decomposition model uses Stan's built-in QR functions in the transformed data block:

```stan
data {
  int<lower=1> N;
  int<lower=1> M;
  matrix[N, M] X;
  vector[N] y;
}

transformed data {
  matrix[N, M] Q_ast;
  matrix[M, M] R_ast;
  matrix[M, M] R_ast_inverse;

  // thin and target-scaled QR decomposition
  Q_ast = qr_thin_Q(X) * sqrt(N - 1);
  R_ast = qr_thin_R(X) / sqrt(N - 1);
  R_ast_inverse = inverse(R_ast);
}

parameters {
  real alpha;
  vector[M] theta;
  real<lower=0> sigma;
}

model {
  theta ~ normal(0, 10);
  alpha ~ normal(0, 10);
  sigma ~ cauchy(0, 10);

  y ~ normal(Q_ast * theta + alpha, sigma);
}

generated quantities {
  vector[M] beta;
  beta = R_ast_inverse * theta;
}
```

Note: The scaling by sqrt(N-1) ensures that Q_ast'Q_ast = I * (N-1) which provides better numerical properties for the sampler.

### Diagnostic Findings

The QR decomposition model shows improved sampling:
- No tree depth saturation
- No divergences
- Higher effective sample sizes
- Better mixing across chains

The QR approach addresses posterior correlations through mathematical reparameterization rather than prior modification, offering a principled computational improvement applicable across diverse regression scenarios.

## Key Takeaway

QR decomposition provides a principled computational strategy for handling correlated covariates by transforming to an orthogonal parameterization, improving MCMC sampling efficiency in Bayesian regression models. This technique is especially valuable when:

- Covariates include polynomial terms (x, x^2, x^3, ...)
- Covariates are naturally correlated (e.g., height and weight)
- The design matrix condition number is large

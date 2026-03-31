# Splines in Stan

**Milad Kharratzadeh** | 24 October 2017

Source: https://mc-stan.org/learn-stan/case-studies/splines_in_stan.html

---

## Overview

This document discusses how to implement splines in Stan. It provides a brief introduction to splines and explains their implementation within Stan, including a novel prior that addresses practical challenges in spline modeling.

## Introduction to Splines

Splines are continuous, piece-wise polynomial functions. B-splines (basis splines) serve as building blocks for spline functions -- any spline function of a given degree can be expressed as a linear combination of B-splines of that degree.

Two parameters uniquely define a family of B-spline functions:
- The polynomial degree, p
- A non-decreasing sequence of knots, t_1, ..., t_q

The order of a spline family equals p + 1.

## B-splines of Order 1

B-splines of order 1 (p=0) form a set of piece-wise constant functions:

    B_{i,1}(x) := { 1  if t_i <= x < t_{i+1}
                   { 0  otherwise

where B_{i,k} denotes the i-th member of a family of B-splines of order k (equivalently, degree k-1).

## Higher-Order B-splines (Recursive Definition)

B-splines of higher orders are defined recursively:

    B_{i,k}(x) := omega_{i,k} * B_{i,k-1}(x) + (1 - omega_{i+1,k}) * B_{i+1,k-1}(x)

where:

    omega_{i,k} := { (x - t_i) / (t_{i+k-1} - t_i)  if t_i != t_{i+k-1}
                    { 0                                 otherwise

At any given point x, a B-spline function of order k represents a linear combination of two B-splines of order k-1.

## Extended Knot Sequences

To establish well-defined B-splines of order k covering the full span of knots (the interval [t_1, t_q)), the knot sequence must be extended as follows:

    extended knots: t_1,...,t_1 (k-1 times), t_1, t_2, t_3, ..., t_q, t_q,...,t_q (k-1 times)

The recursive formulation applies to the extended knots. Without this extension, B-spline functions would not cover areas around the interval edges.

## Second-Order B-splines

Second-order B-splines (B_{i,2}) typically consist of two linear pieces that join continuously at t_{i+1}, forming piecewise linear functions that vanish outside [t_i, t_{i+2}).

## Building the B-spline Basis in R

```r
library(splines)

# Define knots and generate B-spline basis
num_knots <- 10
knots <- seq(from = min(x), to = max(x), length.out = num_knots)
spline_degree <- 3  # cubic splines
num_basis <- num_knots + spline_degree - 1

# Generate B-spline basis matrix using bs()
B <- bs(x, knots = knots[-c(1, num_knots)], degree = spline_degree, intercept = TRUE)

# Or equivalently, using the t() function for the extended knot sequence
B <- t(bs(x, knots = knots[-c(1, num_knots)], degree = spline_degree, intercept = TRUE))
```

## Stan Implementation: Basic Spline Model

```stan
data {
  int num_data;
  int num_basis;
  vector[num_data] y;
  matrix[num_basis, num_data] B;
}

parameters {
  row_vector[num_basis] a_raw;
  real a0;
  real<lower=0> sigma;
  real<lower=0> tau;
}

transformed parameters {
  row_vector[num_basis] a;
  a = a_raw * tau;
}

model {
  // Priors
  a_raw ~ normal(0, 1);
  a0 ~ normal(0, 1);
  tau ~ cauchy(0, 1);
  sigma ~ cauchy(0, 1);

  // Likelihood
  y ~ normal(a0 + a * B, sigma);
}
```

## Novel Prior: Penalizing Second-Order Differences

A key contribution of this case study involves proposing a specialized prior distribution addressing common challenges in spline modeling. This prior encourages smoothness by incorporating information about coefficient relationships, rather than treating each coefficient independently.

The proposed approach uses second-order differences between adjacent coefficients, penalizing abrupt changes:

    a_i - 2*a_{i-1} + a_{i-2} ~ Normal(0, tau)

This creates flexibility while maintaining interpretability and computational stability.

### Stan Implementation with Smoothing Prior

```stan
data {
  int num_data;
  int num_basis;
  vector[num_data] y;
  matrix[num_basis, num_data] B;
}

parameters {
  row_vector[num_basis] a_raw;
  real a0;
  real<lower=0> sigma;
  real<lower=0> tau;
}

transformed parameters {
  row_vector[num_basis] a;
  a = a_raw * tau;
}

model {
  // Smoothing prior on second differences
  a_raw[1] ~ normal(0, 1);
  a_raw[2] ~ normal(0, 1);
  for (i in 3:num_basis)
    a_raw[i] ~ normal(2 * a_raw[i-1] - a_raw[i-2], 1);

  a0 ~ normal(0, 1);
  tau ~ normal(0, 1);
  sigma ~ normal(0, 1);

  // Likelihood
  y ~ normal(a0 + a * B, sigma);
}
```

## Practical Considerations

### Knot Placement

- **Equally spaced knots**: Simplest approach, works well when data is roughly uniformly distributed
- **Quantile-based knots**: Place knots at data quantiles for better coverage of data-dense regions
- **Adaptive knots**: More complex but can capture features at varying scales

### Choosing the Number of Knots

- Too few knots: underfitting, missing important features
- Too many knots: overfitting (mitigated by the smoothing prior)
- The smoothing prior allows using more knots than strictly necessary, as it penalizes overly wiggly fits

### Choosing Spline Degree

- **Degree 1 (linear)**: Piecewise linear, simple but potentially rough
- **Degree 3 (cubic)**: Most common choice, provides smooth curves with continuous first and second derivatives
- **Higher degrees**: Rarely needed in practice

### Connection to Gaussian Processes

The spline model with the second-order difference prior is closely related to Gaussian process regression:
- Both provide flexible nonparametric curve fitting
- Splines are computationally cheaper for 1D problems
- The smoothing prior on B-spline coefficients approximates a GP with a specific covariance structure
- For higher-dimensional problems, GPs may be more natural

## Complete Workflow Example

```r
library(rstan)
library(splines)

# Generate synthetic data
set.seed(1234)
N <- 100
x <- seq(0, 10, length.out = N)
y_true <- sin(x) + 0.5 * cos(2 * x)
y <- y_true + rnorm(N, 0, 0.3)

# Set up B-spline basis
num_knots <- 15
knots <- seq(min(x), max(x), length.out = num_knots)
spline_degree <- 3
B <- t(bs(x, knots = knots[-c(1, num_knots)], degree = spline_degree, intercept = TRUE))
num_basis <- nrow(B)

# Prepare data for Stan
stan_data <- list(
  num_data = N,
  num_basis = num_basis,
  y = y,
  B = B
)

# Fit model
fit <- stan(file = 'spline_model.stan', data = stan_data, iter = 2000, chains = 4)

# Extract and plot results
a <- extract(fit)$a
a0 <- extract(fit)$a0
y_hat <- apply(a, 1, function(ai) a0 + ai %*% B)
y_mean <- colMeans(t(y_hat))

plot(x, y, pch = 16, col = 'grey')
lines(x, y_mean, col = 'blue', lwd = 2)
lines(x, y_true, col = 'red', lwd = 2, lty = 2)
legend('topright', c('Data', 'Fitted', 'True'),
       col = c('grey', 'blue', 'red'), pch = c(16, NA, NA), lty = c(NA, 1, 2))
```

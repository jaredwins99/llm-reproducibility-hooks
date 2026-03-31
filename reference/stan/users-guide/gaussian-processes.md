# Gaussian Processes

## Overview

Gaussian processes are continuous stochastic processes that represent probability distributions over functions. Their defining characteristic is that joint distributions of function values at finite input points follow multivariate normal distributions, making them tractable for model fitting and predictions.

Unlike simple multivariate normal distributions parameterized by mean vectors and covariance matrices, Gaussian processes use mean and covariance functions. These functions map input vectors to mean vectors and covariance matrices for corresponding outputs.

## Gaussian Process Regression

For multivariate Gaussian process regression with N inputs and outputs:

**Mathematical formulation:**

```
y ~ multivariate_normal(m(x), K(x|θ))
```

Where m(x) is an N-vector mean function and K(x|θ) is an N*N positive-definite covariance matrix.

### Popular Covariance Function

The exponentiated quadratic (squared exponential) kernel:

```
K(x|α,ρ,σ)_{i,j} = α^2 exp(-(1/2ρ^2) Σ_d (x_{i,d} - x_{j,d})^2) + δ_{i,j}σ^2
```

**Parameters:**
- α: marginal standard deviation controlling function magnitude
- ρ: length-scale controlling function frequency
- σ: noise scale on diagonal elements

Smaller ρ values yield high-frequency functions; larger values produce smoother, low-frequency functions.

## Simulating from a Gaussian Process

### Basic Univariate Model

```stan
data {
  int<lower=1> N;
  array[N] real x;
}
transformed data {
  matrix[N, N] K = gp_exp_quad_cov(x, 1.0, 1.0);
  vector[N] mu = rep_vector(0, N);
  for (n in 1:N) {
    K[n, n] = K[n, n] + 0.1;
  }
}
parameters {
  vector[N] y;
}
model {
  y ~ multi_normal(mu, K);
}
```

### Multivariate Inputs

Input data declaration changes to:

```stan
data {
  int<lower=1> N;
  int<lower=1> D;
  array[N] vector[D] x;
}
```

The remainder of models remains unchanged, with only distance calculations affected.

### Cholesky Factored Implementation

More efficient implementation using transformed standard normals:

```stan
transformed data {
  matrix[N, N] L;
  // ...
  L = cholesky_decompose(K);
}
parameters {
  vector[N] eta;
}
model {
  eta ~ std_normal();
}
generated quantities {
  vector[N] y;
  y = mu + L * eta;
}
```

For standard normal η and Cholesky decomposition L of K(x|θ):

```
μ + Lη ~ multivariate_normal(μ(x), K(x|θ))
```

## Fitting a Gaussian Process

### GP with Normal Outcomes

**Generative model:**

```
ρ ~ InvGamma(5, 5)
α ~ normal(0, 1)
σ ~ normal(0, 1)
f ~ multivariate_normal(0, K(x|α,ρ))
y_i ~ normal(f_i, σ) for all i
```

**Marginal likelihood formulation** (integrating out f):

```
y ~ multivariate_normal(0, K(x|α,ρ) + I_N σ^2)
```

The marginal approach yields lower-dimensional inference and is computationally more efficient.

### Marginal Likelihood Implementation

```stan
data {
  int<lower=1> N;
  array[N] real x;
  vector[N] y;
}
transformed data {
  vector[N] mu = rep_vector(0, N);
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
}
model {
  matrix[N, N] L_K;
  matrix[N, N] K = gp_exp_quad_cov(x, alpha, rho);
  real sq_sigma = square(sigma);

  for (n in 1:N) {
    K[n, n] = K[n, n] + sq_sigma;
  }

  L_K = cholesky_decompose(K);

  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();

  y ~ multi_normal_cholesky(mu, L_K);
}
```

### Latent Variable GP

For non-normal outcomes, explicit latent variable formulation:

```stan
data {
  int<lower=1> N;
  array[N] real x;
  vector[N] y;
}
transformed data {
  real delta = 1e-9;
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
  vector[N] eta;
}
model {
  vector[N] f;
  {
    matrix[N, N] L_K;
    matrix[N, N] K = gp_exp_quad_cov(x, alpha, rho);

    for (n in 1:N) {
      K[n, n] = K[n, n] + delta;
    }

    L_K = cholesky_decompose(K);
    f = L_K * eta;
  }

  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();
  eta ~ std_normal();

  y ~ normal(f, sigma);
}
```

## Discrete Outcomes with Gaussian Processes

### Poisson GP

For count data, remove σ parameter and use Poisson likelihood with log link:

```stan
data {
  array[N] int<lower=0> y;
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real a;
  vector[N] eta;
}
model {
  // ... (f definition as before)
  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  a ~ std_normal();
  eta ~ std_normal();

  y ~ poisson_log(a + f);
}
```

### Logistic Gaussian Process Regression

For binary classification with z_n in {0,1}:

```
z_n ~ Bernoulli(logit^{-1}(y_n))
```

Implementation:

```stan
data {
  array[N] int<lower=0, upper=1> z;
}
model {
  y ~ bernoulli_logit(a + f);
}
```

## Automatic Relevance Determination

For multivariate inputs, fit dimension-specific length scales ρ_d:

```
k(x|α,ρ,σ)_{i,j} = α^2 exp(-1/2 Σ_d (1/ρ_d^2)(x_{i,d} - x_{j,d})^2) + δ_{i,j}σ^2
```

**Note:** "The magnitude of the scale of the posterior for each ρ_d is dependent on the scaling of the input data along dimension d."

```stan
data {
  int<lower=1> N;
  int<lower=1> D;
  array[N] vector[D] x;
  vector[N] y;
}
transformed data {
  real delta = 1e-9;
}
parameters {
  array[D] real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
  vector[N] eta;
}
model {
  vector[N] f;
  {
    matrix[N, N] L_K;
    matrix[N, N] K = gp_exp_quad_cov(x, alpha, rho);
    for (n in 1:N) {
      K[n, n] = K[n, n] + delta;
    }
    L_K = cholesky_decompose(K);
    f = L_K * eta;
  }

  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();
  eta ~ std_normal();

  y ~ normal(f, sigma);
}
```

## Priors for Gaussian Process Parameters

### Length-Scale Priors

"Unless regularized by a prior, flat likelihood at small length scales induces considerable posterior mass where functions exactly interpolate input data, causing overfitting."

**For standalone GP models:** Use inverse gamma to penalize small length-scales while allowing large ones.

**For GPs with fixed effects:** Use generalized inverse Gaussian with sharper right tail to limit overlap:

```stan
functions {
  real generalized_inverse_gaussian_lpdf(real x, int p,
                                        real a, real b) {
    return p * 0.5 * log(a / b)
      - log(2 * modified_bessel_second_kind(p, sqrt(a * b)))
      + (p - 1) * log(x)
      - (a * x + b / x) * 0.5;
  }
}
```

Zero-crossing statistic: For 1D inputs in domain [0,T], expected zero crossings = T/(πρ).

### Marginal Standard Deviation Priors

Parameter α controls variation explained by the regression function. Use half-t or half-Gaussian priors similar to linear models, allowing non-trivial mass near zero.

## Predictive Inference with Gaussian Processes

### Joint Predictive Sampling

```stan
data {
  int<lower=1> N1;
  array[N1] real x1;
  vector[N1] y1;
  int<lower=1> N2;
  array[N2] real x2;
}
transformed data {
  real delta = 1e-9;
  int<lower=1> N = N1 + N2;
  array[N] real x;
  for (n1 in 1:N1) {
    x[n1] = x1[n1];
  }
  for (n2 in 1:N2) {
    x[N1 + n2] = x2[n2];
  }
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
  vector[N] eta;
}
transformed parameters {
  vector[N] f;
  {
    matrix[N, N] L_K;
    matrix[N, N] K = gp_exp_quad_cov(x, alpha, rho);

    for (n in 1:N) {
      K[n, n] = K[n, n] + delta;
    }

    L_K = cholesky_decompose(K);
    f = L_K * eta;
  }
}
model {
  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();
  eta ~ std_normal();

  y1 ~ normal(f[1:N1], sigma);
}
generated quantities {
  vector[N2] y2;
  for (n2 in 1:N2) {
    y2[n2] = normal_rng(f[N1 + n2], sigma);
  }
}
```

### Non-Gaussian GP Predictive Inference

For logistic GP classification:

```stan
data {
  int<lower=1> N1;
  array[N1] real x1;
  array[N1] int<lower=0, upper=1> z1;
  int<lower=1> N2;
  array[N2] real x2;
}
transformed data {
  real delta = 1e-9;
  int<lower=1> N = N1 + N2;
  array[N] real x;
  for (n1 in 1:N1) {
    x[n1] = x1[n1];
  }
  for (n2 in 1:N2) {
    x[N1 + n2] = x2[n2];
  }
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real a;
  vector[N] eta;
}
transformed parameters {
  vector[N] f;
  {
    matrix[N, N] L_K;
    matrix[N, N] K = gp_exp_quad_cov(x, alpha, rho);

    for (n in 1:N) {
      K[n, n] = K[n, n] + delta;
    }

    L_K = cholesky_decompose(K);
    f = L_K * eta;
  }
}
model {
  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  a ~ std_normal();
  eta ~ std_normal();

  z1 ~ bernoulli_logit(a + f[1:N1]);
}
generated quantities {
  array[N2] int z2;
  for (n2 in 1:N2) {
    z2[n2] = bernoulli_logit_rng(a + f[N1 + n2]);
  }
}
```

### Analytical Predictive Inference

For Gaussian observations, posterior predictive distribution has closed form:

```
p(y_tilde|x_tilde,y,x) = normal(K^T Σ^{-1}y, Ω - K^T Σ^{-1}K)
```

Where:
- Σ = K(x|α,ρ,σ) for observed data
- Ω = K(x_tilde|α,ρ) for prediction inputs
- K = covariance between x and x_tilde

```stan
functions {
  vector gp_pred_rng(array[] real x2,
                     vector y1,
                     array[] real x1,
                     real alpha,
                     real rho,
                     real sigma,
                     real delta) {
    int N1 = rows(y1);
    int N2 = size(x2);
    vector[N2] f2;
    {
      matrix[N1, N1] L_K;
      vector[N1] K_div_y1;
      matrix[N1, N2] k_x1_x2;
      matrix[N1, N2] v_pred;
      vector[N2] f2_mu;
      matrix[N2, N2] cov_f2;
      matrix[N2, N2] diag_delta;
      matrix[N1, N1] K;

      K = gp_exp_quad_cov(x1, alpha, rho);
      for (n in 1:N1) {
        K[n, n] = K[n, n] + square(sigma);
      }
      L_K = cholesky_decompose(K);
      K_div_y1 = mdivide_left_tri_low(L_K, y1);
      K_div_y1 = mdivide_right_tri_low(K_div_y1', L_K)';
      k_x1_x2 = gp_exp_quad_cov(x1, x2, alpha, rho);
      f2_mu = (k_x1_x2' * K_div_y1);
      v_pred = mdivide_left_tri_low(L_K, k_x1_x2);
      cov_f2 = gp_exp_quad_cov(x2, alpha, rho) - v_pred' * v_pred;
      diag_delta = diag_matrix(rep_vector(delta, N2));

      f2 = multi_normal_rng(f2_mu, cov_f2 + diag_delta);
    }
    return f2;
  }
}
data {
  int<lower=1> N1;
  array[N1] real x1;
  vector[N1] y1;
  int<lower=1> N2;
  array[N2] real x2;
}
transformed data {
  vector[N1] mu = rep_vector(0, N1);
  real delta = 1e-9;
}
parameters {
  real<lower=0> rho;
  real<lower=0> alpha;
  real<lower=0> sigma;
}
model {
  matrix[N1, N1] L_K;
  {
    matrix[N1, N1] K = gp_exp_quad_cov(x1, alpha, rho);
    real sq_sigma = square(sigma);

    for (n1 in 1:N1) {
      K[n1, n1] = K[n1, n1] + sq_sigma;
    }

    L_K = cholesky_decompose(K);
  }

  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();

  y1 ~ multi_normal_cholesky(mu, L_K);
}
generated quantities {
  vector[N2] f2;
  vector[N2] y2;

  f2 = gp_pred_rng(x2, y1, x1, alpha, rho, sigma, delta);
  for (n2 in 1:N2) {
    y2[n2] = normal_rng(f2[n2], sigma);
  }
}
```

## Multiple-Output Gaussian Processes

For multivariate outcomes y_i in R^M at inputs x_i in R^K:

```
y_i ~ multivariate_normal(f(x_i), I_M σ^2)
f(x) ~ GP(m(x), K(x|θ,φ))
```

With separable kernel:

```
K(x,x'|θ,φ)_{[m,m']} = k(x,x'|θ)k(m,m'|φ)
```

Finite-dimensional model using matrix normal distribution:

```
f ~ matrixnormal(m(x), K(x|α,ρ), C(φ))
y_{i,m} ~ normal(f_{i,m}, σ)
f in R^{N*M}
```

The matrix normal has rows:

```
f_{[n,]} ~ multivariate_normal(m(x)_{[n,]}, K(x|α,ρ)_{[n,n]} C(φ))
```

And columns:

```
f_{[,m]} ~ multivariate_normal(m(x)_{[,m]}, K(x|α,ρ) C(φ)_{[m,m]})
```

**Constraint:** Set α = 1.0 because parameters are not identified otherwise (multiply α by d and C by 1/d yields same likelihood).

Sampling algorithm:

```
η_{i,j} ~ normal(0,1) for all i,j
f = L_{K(x|1.0,ρ)} η L_C(φ)^T
```

Implementation:

```stan
data {
  int<lower=1> N;
  int<lower=1> D;
  array[N] real x;
  matrix[N, D] y;
}
transformed data {
  real delta = 1e-9;
}
parameters {
  real<lower=0> rho;
  vector<lower=0>[D] alpha;
  real<lower=0> sigma;
  cholesky_factor_corr[D] L_Omega;
  matrix[N, D] eta;
}
model {
  matrix[N, D] f;
  {
    matrix[N, N] K = gp_exp_quad_cov(x, 1.0, rho);
    matrix[N, N] L_K;

    for (n in 1:N) {
      K[n, n] = K[n, n] + delta;
    }

    L_K = cholesky_decompose(K);
    f = L_K * eta
        * diag_pre_multiply(alpha, L_Omega)';
  }

  rho ~ inv_gamma(5, 5);
  alpha ~ std_normal();
  sigma ~ std_normal();
  L_Omega ~ lkj_corr_cholesky(3);
  to_vector(eta) ~ std_normal();

  to_vector(y) ~ normal(to_vector(f), sigma);
}
generated quantities {
  matrix[D, D] Omega;
  Omega = L_Omega * L_Omega';
}
```

## Computational Considerations

"Fitting Gaussian processes using exact inference by computing Cholesky of the covariance matrix scales cubicly with the size of data. Gaussian processes using exact inference with N>1000 are too slow for practical purposes in Stan."

Cholesky-parameterized multivariate normal is preferred over standard parameterization for N >= 100 due to optimized implementation.

Hamiltonian Monte Carlo is effective for hyperparameter inference. Well-concentrated posteriors enable fitting models with hundreds of data points in seconds.

## References

- Neal, Radford M. 1996. *Bayesian Learning for Neural Networks*. Springer.
- Neal, Radford M. 1997. "Monte Carlo Implementation of Gaussian Process Models."
- Piironen, Juho, and Aki Vehtari. 2016. "Projection Predictive Model Selection for Gaussian Processes."
- Rasmussen, Carl Edward, and Christopher K. I. Williams. 2006. *Gaussian Processes for Machine Learning*. MIT Press.
- Riutort-Mayol, Gabriel, et al. 2023. "Practical Hilbert Space Approximate Bayesian Gaussian Processes."
- Zhang, Hao. 2004. "Inconsistent Estimation and Asymptotically Equal Interpolations."

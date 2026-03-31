# Distributions over Unbounded Vectors

## Overview

This page documents probability distributions with support on all of R^K for some fixed K.

## Multivariate Normal Distribution

### Probability Density Function

For K in N, mu in R^K, and Sigma in R^(KxK) symmetric and positive definite, the density is:

MultiNormal(y|mu,Sigma) = (1/(2*pi)^(K/2)) * (1/sqrt(|Sigma|)) * exp(-(1/2)(y-mu)^T Sigma^{-1} (y-mu))

### Distribution Statement

```stan
y ~ multi_normal(mu, Sigma)
```

*Available since 2.0*

### Stan Functions

**Probability Density Functions:**

- `real multi_normal_lpdf(vectors y | vectors mu, matrix Sigma)` - Log density (Available since 2.12)
- `real multi_normal_lupdf(vectors y | vectors mu, matrix Sigma)` - Log density without constants (Available since 2.25)
- Row vector variants also available for both y and mu

**Random Number Generation:**

- `vector multi_normal_rng(vector mu, matrix Sigma)` - Single variate (Available since 2.0)
- `vectors multi_normal_rng(vectors mu, matrix Sigma)` - Array of variates (Available since 2.18)

---

## Multivariate Normal Distribution, Precision Parameterization

### Probability Density Function

For K in N, mu in R^K, and Omega in R^(KxK) symmetric and positive definite:

MultiNormalPrecision(y|mu,Omega) = MultiNormal(y|mu,Omega^{-1})

### Distribution Statement

```stan
y ~ multi_normal_prec(mu, Omega)
```

*Available since 2.3*

### Stan Functions

- `real multi_normal_prec_lpdf(vectors y | vectors mu, matrix Omega)` - Log density (Available since 2.18)
- `real multi_normal_prec_lupdf(vectors y | vectors mu, matrix Omega)` - Without constants (Available since 2.25)
- Row vector variants also available

---

## Multivariate Normal Distribution, Cholesky Parameterization

### Probability Density Function

For K in N, mu in R^K, and L in R^(KxK) lower triangular with LL^T positive definite:

MultiNormalCholesky(y|mu,L) = MultiNormal(y|mu,LL^T)

The diagonal elements L_{k,k} must be strictly positive for k in 1:K.

### Distribution Statement

```stan
y ~ multi_normal_cholesky(mu, L)
```

*Available since 2.0*

### Stan Functions

- `real multi_normal_cholesky_lpdf(vectors y | vectors mu, matrix L)` - Log density (Available since 2.18)
- `real multi_normal_cholesky_lupdf(vectors y | vectors mu, matrix L)` - Without constants (Available since 2.25)
- Row vector variants also available
- `vector multi_normal_cholesky_rng(vector mu, matrix L)` - Single variate (Available since 2.3)
- `vectors multi_normal_cholesky_rng(vectors mu, matrix L)` - Array of variates (Available since 2.18)

---

## Multivariate Gaussian Process Distribution

### Probability Density Function

For K, N in N, Sigma in R^(NxN) symmetric positive definite kernel matrix, and w in R^K vector of positive inverse scales:

MultiGP(y|Sigma,w) = prod_{i=1}^K MultiNormal(y_i|0,w_i^{-1} Sigma)

where y_i is the i-th row of y. Used for Gaussian Processes with multivariate outputs where output dimensions share a kernel function but vary by scale.

### Distribution Statement

```stan
y ~ multi_gp(Sigma, w)
```

*Available since 2.3*

### Stan Functions

- `real multi_gp_lpdf(matrix y | matrix Sigma, vector w)` - Log density (Available since 2.12)
- `real multi_gp_lupdf(matrix y | matrix Sigma, vector w)` - Without constants (Available since 2.25)

---

## Multivariate Gaussian Process Distribution, Cholesky Parameterization

### Probability Density Function

MultiGPCholesky(y|L,w) = prod_{i=1}^K MultiNormal(y_i|0,w_i^{-1} LL^T)

More efficient than MultiGP when kernel Cholesky factor is available.

### Distribution Statement

```stan
y ~ multi_gp_cholesky(L, w)
```

*Available since 2.5*

### Stan Functions

- `real multi_gp_cholesky_lpdf(matrix y | matrix L, vector w)` - Log density (Available since 2.12)
- `real multi_gp_cholesky_lupdf(matrix y | matrix L, vector w)` - Without constants (Available since 2.25)

---

## Multivariate Student-t Distribution

### Probability Density Function

For K in N, nu in R+, mu in R^K, and Sigma in R^(KxK) symmetric positive definite:

MultiStudentT(y|nu,mu,Sigma) = (1/pi^(K/2)) * (1/nu^(K/2)) * (Gamma((nu+K)/2)/Gamma(nu/2)) * (1/sqrt(|Sigma|)) * (1 + (1/nu)(y-mu)^T Sigma^{-1} (y-mu))^(-(nu+K)/2)

### Distribution Statement

```stan
y ~ multi_student_t(nu, mu, Sigma)
```

*Available since 2.0*

### Stan Functions

- `real multi_student_t_lpdf(vectors y | real nu, vectors mu, matrix Sigma)` - Log density (Available since 2.18)
- `real multi_student_t_lupdf(vectors y | real nu, vectors mu, matrix Sigma)` - Without constants (Available since 2.25)
- Row vector variants also available
- `vector multi_student_t_rng(real nu, vector mu, matrix Sigma)` - Single variate (Available since 2.0)
- `vectors multi_student_t_rng(real nu, vectors mu, matrix Sigma)` - Array of variates (Available since 2.18)

---

## Multivariate Student-t Distribution, Cholesky Parameterization

### Probability Density Function

MultiStudentTCholesky(y|nu,mu,L) uses Cholesky factor L instead of full covariance matrix.

### Distribution Statement

```stan
y ~ multi_student_t_cholesky(nu, mu, L)
```

*Available since 2.30*

### Stan Functions

- `real multi_student_t_cholesky_lpdf(vectors y | real nu, vectors mu, matrix L)` - Log density (Available since 2.30)
- `real multi_student_t_cholesky_lupdf(vectors y | real nu, vectors mu, matrix L)` - Without constants (Available since 2.30)
- `vector multi_student_t_cholesky_rng(real nu, vector mu, matrix L)` - Single variate (Available since 2.30)
- `array[] vector multi_student_t_cholesky_rng(real nu, array[] vector mu, matrix L)` - Array of variates (Available since 2.30)

---

## Gaussian Dynamic Linear Models

A Gaussian Dynamic Linear Model is defined for t in 1, ..., T as:

```
y_t ~ N(F' theta_t, V)
theta_t ~ N(G theta_{t-1}, W)
theta_0 ~ N(m_0, C_0)
```

where y is an n x T matrix with rows as variables and columns as observations. These functions calculate the log-density of observations marginalizing over latent states using the Kalman Filter. When V is diagonal, a more efficient sequential algorithm avoiding matrix inversions is used.

### Distribution Statement

```stan
y ~ gaussian_dlm_obs(F, G, V, W, m0, C0)
```

*Available since 2.0*

### Stan Functions

**Full Covariance:**
- `real gaussian_dlm_obs_lpdf(matrix y | matrix F, matrix G, matrix V, matrix W, vector m0, matrix C0)` (Available since 2.12)
- `real gaussian_dlm_obs_lupdf(matrix y | matrix F, matrix G, matrix V, matrix W, vector m0, matrix C0)` (Available since 2.25)

**Diagonal Covariance:**
- `real gaussian_dlm_obs_lpdf(matrix y | matrix F, matrix G, vector V, matrix W, vector m0, matrix C0)` (Available since 2.12)
- `real gaussian_dlm_obs_lupdf(matrix y | matrix F, matrix G, vector V, matrix W, vector m0, matrix C0)` (Available since 2.25)

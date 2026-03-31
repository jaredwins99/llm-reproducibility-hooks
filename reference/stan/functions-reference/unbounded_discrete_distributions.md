# Unbounded Discrete Distributions - Complete Content

## Overview

The unbounded discrete distributions have support over the natural numbers (i.e., the non-negative integers).

---

## Negative Binomial Distribution

### Probability Mass Function

For alpha in R+, beta in R+, and n in N:

NegBinomial(n|alpha,beta) = C(n + alpha - 1, alpha - 1) * (beta/(beta+1))^alpha * (1/(beta + 1))^n

Mean: E[n] = alpha/beta
Variance: Var[n] = (alpha/beta^2)(beta + 1)

### Distribution Statement

```stan
n ~ neg_binomial(alpha, beta)
```

### Stan Functions

- `real neg_binomial_lpmf(ints n | reals alpha, reals beta)` - Log probability mass (Available since 2.12)
- `real neg_binomial_lupmf(ints n | reals alpha, reals beta)` - Log probability mass dropping constants (Available since 2.25)
- `real neg_binomial_cdf(ints n | reals alpha, reals beta)` - CDF (Available since 2.0)
- `real neg_binomial_lcdf(ints n | reals alpha, reals beta)` - Log CDF (Available since 2.12)
- `real neg_binomial_lccdf(ints n | reals alpha, reals beta)` - Log complementary CDF (Available since 2.12)
- `R neg_binomial_rng(reals alpha, reals beta)` - Generate random variate; alpha/beta must be < 2^29 (Available since 2.18)

---

## Negative Binomial Distribution (Alternative Parameterization)

### Probability Mass Function

For mu in R+, phi in R+, and n in N:

NegBinomial2(n | mu, phi) = C(n + phi - 1, n) * (mu/(mu+phi))^n * (phi/(mu+phi))^phi

Mean: E[n] = mu
Variance: Var[n] = mu + mu^2/phi

### Distribution Statement

```stan
n ~ neg_binomial_2(mu, phi)
```

### Stan Functions

- `real neg_binomial_2_lpmf(ints n | reals mu, reals phi)` - Log probability mass (Available since 2.20)
- `real neg_binomial_2_lupmf(ints n | reals mu, reals phi)` - Log probability mass dropping constants (Available since 2.25)
- `real neg_binomial_2_cdf(ints n | reals mu, reals phi)` - CDF (Available since 2.6)
- `real neg_binomial_2_lcdf(ints n | reals mu, reals phi)` - Log CDF (Available since 2.12)
- `real neg_binomial_2_lccdf(ints n | reals mu, reals phi)` - Log complementary CDF (Available since 2.12)
- `R neg_binomial_2_rng(reals mu, reals phi)` - Generate random variate; mu must be < 2^29 (Available since 2.18)

---

## Negative Binomial Distribution (Log Alternative Parameterization)

For eta in R, phi in R+, n in N:

NegBinomial2Log(n | eta, phi) = NegBinomial2(n | exp(eta), phi)

### Distribution Statement

```stan
n ~ neg_binomial_2_log(eta, phi)
```

### Stan Functions

- `real neg_binomial_2_log_lpmf(ints n | reals eta, reals phi)` - Log probability mass (Available since 2.20)
- `real neg_binomial_2_log_lupmf(ints n | reals eta, reals phi)` - Log probability mass dropping constants (Available since 2.25)
- `R neg_binomial_2_log_rng(reals eta, reals phi)` - Generate random variate; eta must be < 29 log 2 (Available since 2.18)

---

## Negative-Binomial-2-Log Generalized Linear Model

### Probability Mass Function

For x in R^{n x m}, alpha in R^n, beta in R^m, phi in R+, y in N^n:

NegBinomial2LogGLM(y|x, alpha, beta, phi) = prod(1<=i<=n) NegBinomial2(y_i|exp(alpha_i + x_i*beta), phi)

### Distribution Statement

```stan
y ~ neg_binomial_2_log_glm(x, alpha, beta, phi)
```

### Stan Functions

Multiple overloads for different argument types:

- `real neg_binomial_2_log_glm_lpmf(int y | matrix x, real alpha, vector beta, real phi)` (Available since 2.23)
- `real neg_binomial_2_log_glm_lupmf(int y | matrix x, real alpha, vector beta, real phi)` (Available since 2.25)
- `real neg_binomial_2_log_glm_lpmf(int y | matrix x, vector alpha, vector beta, real phi)` (Available since 2.23)
- `real neg_binomial_2_log_glm_lupmf(int y | matrix x, vector alpha, vector beta, real phi)` (Available since 2.25)
- `real neg_binomial_2_log_glm_lpmf(array[] int y | row_vector x, real alpha, vector beta, real phi)` (Available since 2.23)
- `real neg_binomial_2_log_glm_lupmf(array[] int y | row_vector x, real alpha, vector beta, real phi)` (Available since 2.25)
- `real neg_binomial_2_log_glm_lpmf(array[] int y | row_vector x, vector alpha, vector beta, real phi)` (Available since 2.23)
- `real neg_binomial_2_log_glm_lupmf(array[] int y | row_vector x, vector alpha, vector beta, real phi)` (Available since 2.25)
- `real neg_binomial_2_log_glm_lpmf(array[] int y | matrix x, real alpha, vector beta, real phi)` (Available since 2.18)
- `real neg_binomial_2_log_glm_lupmf(array[] int y | matrix x, real alpha, vector beta, real phi)` (Available since 2.25)
- `real neg_binomial_2_log_glm_lpmf(array[] int y | matrix x, vector alpha, vector beta, real phi)` (Available since 2.18)
- `real neg_binomial_2_log_glm_lupmf(array[] int y | matrix x, vector alpha, vector beta, real phi)` (Available since 2.25)

---

## Poisson Distribution

### Probability Mass Function

For lambda in R+, n in N:

Poisson(n|lambda) = (1/n!) * lambda^n * exp(-lambda)

### Distribution Statement

```stan
n ~ poisson(lambda)
```

### Stan Functions

- `real poisson_lpmf(ints n | reals lambda)` - Log probability mass (Available since 2.12)
- `real poisson_lupmf(ints n | reals lambda)` - Log probability mass dropping constants (Available since 2.25)
- `real poisson_cdf(ints n | reals lambda)` - CDF (Available since 2.0)
- `real poisson_lcdf(ints n | reals lambda)` - Log CDF (Available since 2.12)
- `real poisson_lccdf(ints n | reals lambda)` - Log complementary CDF (Available since 2.12)
- `R poisson_rng(reals lambda)` - Generate random variate; lambda must be < 2^30 (Available since 2.18)

---

## Poisson Distribution, Log Parameterization

For alpha in R, n in N:

PoissonLog(n|alpha) = (1/n!) * exp(n*alpha - exp(alpha))

### Distribution Statement

```stan
n ~ poisson_log(alpha)
```

### Stan Functions

- `real poisson_log_lpmf(ints n | reals alpha)` - Log probability mass (Available since 2.12)
- `real poisson_log_lupmf(ints n | reals alpha)` - Log probability mass dropping constants (Available since 2.25)
- `R poisson_log_rng(reals alpha)` - Generate random variate; alpha must be < 30 log 2 (Available since 2.18)

---

## Poisson-Log Generalized Linear Model

### Probability Mass Function

For x in R^{n x m}, alpha in R^n, beta in R^m, y in N^n:

PoissonLogGLM(y|x, alpha, beta) = prod(1<=i<=n) Poisson(y_i|exp(alpha_i + x_i*beta))

### Distribution Statement

```stan
y ~ poisson_log_glm(x, alpha, beta)
```

### Stan Functions

Multiple overloads:

- `real poisson_log_glm_lpmf(int y | matrix x, real alpha, vector beta)` (Available since 2.23)
- `real poisson_log_glm_lupmf(int y | matrix x, real alpha, vector beta)` (Available since 2.25)
- `real poisson_log_glm_lpmf(int y | matrix x, vector alpha, vector beta)` (Available since 2.23)
- `real poisson_log_glm_lupmf(int y | matrix x, vector alpha, vector beta)` (Available since 2.25)
- `real poisson_log_glm_lpmf(array[] int y | row_vector x, real alpha, vector beta)` (Available since 2.23)
- `real poisson_log_glm_lupmf(array[] int y | row_vector x, real alpha, vector beta)` (Available since 2.25)
- `real poisson_log_glm_lpmf(array[] int y | row_vector x, vector alpha, vector beta)` (Available since 2.23)
- `real poisson_log_glm_lupmf(array[] int y | row_vector x, vector alpha, vector beta)` (Available since 2.25)
- `real poisson_log_glm_lpmf(array[] int y | matrix x, real alpha, vector beta)` (Available since 2.18)
- `real poisson_log_glm_lupmf(array[] int y | matrix x, real alpha, vector beta)` (Available since 2.25)
- `real poisson_log_glm_lpmf(array[] int y | matrix x, vector alpha, vector beta)` (Available since 2.18)
- `real poisson_log_glm_lupmf(array[] int y | matrix x, vector alpha, vector beta)` (Available since 2.25)

---

## Beta Negative Binomial Distribution

### Probability Mass Function

For r in R+, alpha in R+, beta in R+, n in N:

BetaNegBinomial(n|r,alpha,beta) = [Gamma(n+r)/(n!*Gamma(r))] * [B(beta+n,alpha+r)/B(beta,alpha)]

### Distribution Statement

```stan
n ~ beta_neg_binomial(r, alpha, beta)
```

### Stan Functions

- `real beta_neg_binomial_lpmf(ints n | reals r, reals alpha, reals beta)` - Log probability mass (Available since 2.36)
- `real beta_neg_binomial_lupmf(ints n | reals r, reals alpha, reals beta)` - Log probability mass dropping constants (Available since 2.36)
- `real beta_neg_binomial_cdf(ints n | reals r, reals alpha, reals beta)` - CDF (Available since 2.36)
- `real beta_neg_binomial_lcdf(ints n | reals r, reals alpha, reals beta)` - Log CDF (Available since 2.36)
- `real beta_neg_binomial_lccdf(ints n | reals r, reals alpha, reals beta)` - Log complementary CDF (Available since 2.36)
- `R beta_neg_binomial_rng(reals r, reals alpha, reals beta)` - Generate random variate; r*beta/(alpha-1) must be < 2^29 (Available since 2.36)

---

## Reference

Gelman, Andrew, J. B. Carlin, Hal S. Stern, David B. Dunson, Aki Vehtari, and Donald B. Rubin. 2013. *Bayesian Data Analysis*. Third Edition. London: Chapman & Hall / CRC Press.

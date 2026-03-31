# Unbounded Continuous Distributions

## Overview

The unbounded univariate continuous probability distributions have support on all real numbers.

---

## Normal Distribution

### Probability Density Function

For mu in R and sigma in R+, the density is:

Normal(y|mu,sigma) = (1/(sqrt(2*pi) * sigma)) * exp(-(1/2)((y-mu)/sigma)^2)

### Distribution Statement

```stan
y ~ normal(mu, sigma)
```

### Stan Functions

- `real normal_lpdf(reals y | reals mu, reals sigma)` - Log probability density (available since 2.12)
- `real normal_lupdf(reals y | reals mu, reals sigma)` - Log density dropping constants (available since 2.25)
- `real normal_cdf(reals y | reals mu, reals sigma)` - CDF (available since 2.0)
- `real normal_lcdf(reals y | reals mu, reals sigma)` - Log CDF (available since 2.12)
- `real normal_lccdf(reals y | reals mu, reals sigma)` - Log complementary CDF (available since 2.15)
- `R normal_rng(reals mu, reals sigma)` - Random number generation (available since 2.18)

---

## Standard Normal Distribution

The standard normal has mu = 0 and sigma = 1, providing computational efficiency:

log Normal(y|0,1) = -y^2/2 + const

### Distribution Statement

```stan
y ~ std_normal()
```

### Stan Functions

- `real std_normal_lpdf(reals y)` - Log probability density (available since 2.18)
- `real std_normal_lupdf(reals y)` - Log density dropping constants (available since 2.25)
- `real std_normal_cdf(reals y)` - CDF (available since 2.21)
- `real std_normal_lcdf(reals y)` - Log CDF (available since 2.21)
- `real std_normal_lccdf(reals y)` - Log complementary CDF (available since 2.21)
- `R std_normal_qf(T x)` - Quantile function, inverse standard normal CDF (available since 2.31)
- `R std_normal_log_qf(T x)` - Log quantile function (available since 2.31)
- `real std_normal_rng()` - Random number generation (available since 2.21)

---

## Normal-ID Generalized Linear Model (Linear Regression)

Efficient implementation for linear regression with normal distribution and identity link.

### Probability Distribution Function

For x in R^{n x m}, alpha in R^n, beta in R^m, sigma in R+:

NormalIdGLM(y|x,alpha,beta,sigma) = prod Normal(y_i|alpha_i + x_i*beta, sigma)

### Distribution Statement

```stan
y ~ normal_id_glm(x, alpha, beta, sigma)
```

### Stan Functions

Multiple overloads available with scalar/vector alpha and scalar/vector sigma:

- `real normal_id_glm_lpdf(real y | matrix x, real alpha, vector beta, real sigma)` (available since 2.29)
- `real normal_id_glm_lupdf(real y | matrix x, real alpha, vector beta, real sigma)` (available since 2.29)
- `real normal_id_glm_lpdf(vector y | matrix x, real alpha, vector beta, real sigma)` (available since 2.23)
- `real normal_id_glm_lupdf(vector y | matrix x, real alpha, vector beta, real sigma)` (available since 2.23)
- `real normal_id_glm_lpdf(vector y | row_vector x, real alpha, vector beta, real sigma)` (available since 2.29)
- `real normal_id_glm_lupdf(vector y | row_vector x, real alpha, vector beta, real sigma)` (available since 2.29)

(Plus additional overloads with vector alpha and vector sigma variants)

---

## Exponentially Modified Normal Distribution

Distribution of Z = X + Y where X is normally distributed (mu, sigma) and Y is exponentially distributed (rate lambda).

### Probability Density Function

For mu in R, sigma in R+, lambda in R+:

ExpModNormal(y|mu,sigma,lambda) = (lambda/2) * exp((lambda/2)(2*mu + lambda*sigma^2 - 2y)) * erfc((mu + lambda*sigma^2 - y)/(sqrt(2)*sigma))

### Distribution Statement

```stan
y ~ exp_mod_normal(mu, sigma, lambda)
```

### Stan Functions

- `real exp_mod_normal_lpdf(reals y | reals mu, reals sigma, reals lambda)` (available since 2.18)
- `real exp_mod_normal_lupdf(reals y | reals mu, reals sigma, reals lambda)` (available since 2.25)
- `real exp_mod_normal_cdf(reals y | reals mu, reals sigma, reals lambda)` (available since 2.0)
- `real exp_mod_normal_lcdf(reals y | reals mu, reals sigma, reals lambda)` (available since 2.18)
- `real exp_mod_normal_lccdf(reals y | reals mu, reals sigma, reals lambda)` (available since 2.18)
- `R exp_mod_normal_rng(reals mu, reals sigma, reals lambda)` (available since 2.18)

---

## Skew Normal Distribution

### Probability Density Function

For xi in R, omega in R+, alpha in R:

SkewNormal(y|xi,omega,alpha) = (1/(omega*sqrt(2*pi))) * exp(-(1/2)((y-xi)/omega)^2) * (1 + erf(alpha*((y-xi)/(omega*sqrt(2)))))

### Distribution Statement

```stan
y ~ skew_normal(xi, omega, alpha)
```

### Stan Functions

- `real skew_normal_lpdf(reals y | reals xi, reals omega, reals alpha)` (available since 2.16)
- `real skew_normal_lupdf(reals y | reals xi, reals omega, reals alpha)` (available since 2.25)
- `real skew_normal_cdf(reals y | reals xi, reals omega, reals alpha)` (available since 2.16)
- `real skew_normal_lcdf(reals y | reals xi, reals omega, reals alpha)` (available since 2.18)
- `real skew_normal_lccdf(reals y | reals xi, reals omega, reals alpha)` (available since 2.18)
- `R skew_normal_rng(reals xi, reals omega, real alpha)` (available since 2.18)

---

## Student-t Distribution

### Probability Density Function

For nu in R+, mu in R, sigma in R+:

StudentT(y|nu,mu,sigma) = Gamma((nu+1)/2) / (Gamma(nu/2)*sqrt(nu*pi)*sigma) * (1 + (1/nu)*((y-mu)/sigma)^2)^(-(nu+1)/2)

### Distribution Statement

```stan
y ~ student_t(nu, mu, sigma)
```

### Stan Functions

- `real student_t_lpdf(reals y | reals nu, reals mu, reals sigma)` (available since 2.12)
- `real student_t_lupdf(reals y | reals nu, reals mu, reals sigma)` (available since 2.25)
- `real student_t_cdf(reals y | reals nu, reals mu, reals sigma)` (available since 2.0)
- `real student_t_lcdf(reals y | reals nu, reals mu, reals sigma)` (available since 2.12)
- `real student_t_lccdf(reals y | reals nu, reals mu, reals sigma)` (available since 2.12)
- `R student_t_rng(reals nu, reals mu, reals sigma)` (available since 2.18)

---

## Cauchy Distribution

### Probability Density Function

For mu in R, sigma in R+:

Cauchy(y|mu,sigma) = (1/(pi*sigma)) * (1/(1 + ((y-mu)/sigma)^2))

### Distribution Statement

```stan
y ~ cauchy(mu, sigma)
```

### Stan Functions

- `real cauchy_lpdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real cauchy_lupdf(reals y | reals mu, reals sigma)` (available since 2.25)
- `real cauchy_cdf(reals y | reals mu, reals sigma)` (available since 2.0)
- `real cauchy_lcdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real cauchy_lccdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `R cauchy_rng(reals mu, reals sigma)` (available since 2.18)

---

## Double Exponential (Laplace) Distribution

### Probability Density Function

For mu in R, sigma in R+:

DoubleExponential(y|mu,sigma) = (1/(2*sigma)) * exp(-|y-mu|/sigma)

**Note:** Parameterized by scale sigma, contrasting with the exponential distribution's inverse scale parameterization.

### Compound Representation

Can be expressed as a compound exponential-normal distribution:

```
alpha ~ Exponential(1/(2*sigma^2))
beta|alpha ~ Normal(mu, sqrt(alpha))
beta ~ DoubleExponential(mu, sigma)
```

### Distribution Statement

```stan
y ~ double_exponential(mu, sigma)
```

### Stan Functions

- `real double_exponential_lpdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real double_exponential_lupdf(reals y | reals mu, reals sigma)` (available since 2.25)
- `real double_exponential_cdf(reals y | reals mu, reals sigma)` (available since 2.0)
- `real double_exponential_lcdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real double_exponential_lccdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `R double_exponential_rng(reals mu, reals sigma)` (available since 2.18)

---

## Logistic Distribution

### Probability Density Function

For mu in R, sigma in R+:

Logistic(y|mu,sigma) = (1/sigma) * exp(-(y-mu)/sigma) * (1 + exp(-(y-mu)/sigma))^(-2)

### Distribution Statement

```stan
y ~ logistic(mu, sigma)
```

### Stan Functions

- `real logistic_lpdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real logistic_lupdf(reals y | reals mu, reals sigma)` (available since 2.25)
- `real logistic_cdf(reals y | reals mu, reals sigma)` (available since 2.0)
- `real logistic_lcdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `real logistic_lccdf(reals y | reals mu, reals sigma)` (available since 2.12)
- `R logistic_rng(reals mu, reals sigma)` (available since 2.18)

---

## Gumbel Distribution

### Probability Density Function

For mu in R, beta in R+:

Gumbel(y|mu,beta) = (1/beta) * exp(-(y-mu)/beta - exp(-(y-mu)/beta))

### Distribution Statement

```stan
y ~ gumbel(mu, beta)
```

### Stan Functions

- `real gumbel_lpdf(reals y | reals mu, reals beta)` (available since 2.12)
- `real gumbel_lupdf(reals y | reals mu, reals beta)` (available since 2.25)
- `real gumbel_cdf(reals y | reals mu, reals beta)` (available since 2.0)
- `real gumbel_lcdf(reals y | reals mu, reals beta)` (available since 2.12)
- `real gumbel_lccdf(reals y | reals mu, reals beta)` (available since 2.12)
- `R gumbel_rng(reals mu, reals beta)` (available since 2.18)

---

## Skew Double Exponential Distribution

### Probability Density Function

For mu in R, sigma in R+, tau in [0,1]:

SkewDoubleExponential(y|mu,sigma,tau) = (2*tau*(1-tau)/sigma) * exp(-(2/sigma)[(1-tau)*I(y<mu)*(mu-y) + tau*I(y>mu)*(y-mu)])

### Distribution Statement

```stan
y ~ skew_double_exponential(mu, sigma, tau)
```

### Stan Functions

- `real skew_double_exponential_lpdf(reals y | reals mu, reals sigma, reals tau)` (available since 2.28)
- `real skew_double_exponential_lupdf(reals y | reals mu, reals sigma, reals tau)` (available since 2.28)
- `real skew_double_exponential_cdf(reals y | reals mu, reals sigma, reals tau)` (available since 2.28)
- `real skew_double_exponential_lcdf(reals y | reals mu, reals sigma, reals tau)` (available since 2.28)
- `real skew_double_exponential_lccdf(reals y | reals mu, reals sigma, reals tau)` (available since 2.28)
- `R skew_double_exponential_rng(reals mu, reals sigma, reals tau)` (available since 2.28)

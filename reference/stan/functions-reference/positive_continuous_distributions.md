# Positive Continuous Distributions - Stan Functions Reference

## Overview

"The positive continuous probability functions have support on the positive real numbers."

## Lognormal Distribution

### Probability Density Function

For parameters mu in R and sigma in R+, with y in R+:

LogNormal(y|mu,sigma) = (1/(sqrt(2*pi) * sigma)) * (1/y) * exp(-(1/2)((log y - mu)/sigma)^2)

### Distribution Statement

`y ~ lognormal(mu, sigma)` - Available since 2.0

### Stan Functions

- `real lognormal_lpdf(reals y | reals mu, reals sigma)` - Log density (Available since 2.12)
- `real lognormal_lupdf(reals y | reals mu, reals sigma)` - Log density dropping constants (Available since 2.25)
- `real lognormal_cdf(reals y | reals mu, reals sigma)` - CDF (Available since 2.0)
- `real lognormal_lcdf(reals y | reals mu, reals sigma)` - Log CDF (Available since 2.12)
- `real lognormal_lccdf(reals y | reals mu, reals sigma)` - Log complementary CDF (Available since 2.12)
- `R lognormal_rng(reals mu, reals sigma)` - Random variate generation (Available since 2.22)

## Chi-Square Distribution

### Probability Density Function

For parameter nu in R+, with y in R+:

ChiSquare(y|nu) = (2^(-nu/2) / Gamma(nu/2)) * y^(nu/2 - 1) * exp(-y/2)

### Distribution Statement

`y ~ chi_square(nu)` - Available since 2.0

### Stan Functions

- `real chi_square_lpdf(reals y | reals nu)` - Log density (Available since 2.12)
- `real chi_square_lupdf(reals y | reals nu)` - Log density dropping constants (Available since 2.25)
- `real chi_square_cdf(reals y | reals nu)` - CDF (Available since 2.0)
- `real chi_square_lcdf(reals y | reals nu)` - Log CDF (Available since 2.12)
- `real chi_square_lccdf(reals y | reals nu)` - Log complementary CDF (Available since 2.12)
- `R chi_square_rng(reals nu)` - Random variate generation (Available since 2.18)

## Inverse Chi-Square Distribution

### Probability Density Function

For parameter nu in R+, with y in R+:

InvChiSquare(y|nu) = (2^(-nu/2) / Gamma(nu/2)) * y^(-nu/2 - 1) * exp(-1/(2y))

### Distribution Statement

`y ~ inv_chi_square(nu)` - Available since 2.0

### Stan Functions

- `real inv_chi_square_lpdf(reals y | reals nu)` - Log density (Available since 2.12)
- `real inv_chi_square_lupdf(reals y | reals nu)` - Log density dropping constants (Available since 2.25)
- `real inv_chi_square_cdf(reals y | reals nu)` - CDF (Available since 2.0)
- `real inv_chi_square_lcdf(reals y | reals nu)` - Log CDF (Available since 2.12)
- `real inv_chi_square_lccdf(reals y | reals nu)` - Log complementary CDF (Available since 2.12)
- `R inv_chi_square_rng(reals nu)` - Random variate generation (Available since 2.18)

## Scaled Inverse Chi-Square Distribution

### Probability Density Function

For parameters nu in R+ and sigma in R+, with y in R+:

ScaledInvChiSquare(y|nu,sigma) = ((nu/2)^(nu/2) / Gamma(nu/2)) * sigma^nu * y^(-(nu/2 + 1)) * exp(-(nu*sigma^2)/(2y))

### Distribution Statement

`y ~ scaled_inv_chi_square(nu, sigma)` - Available since 2.0

### Stan Functions

- `real scaled_inv_chi_square_lpdf(reals y | reals nu, reals sigma)` - Log density (Available since 2.12)
- `real scaled_inv_chi_square_lupdf(reals y | reals nu, reals sigma)` - Log density dropping constants (Available since 2.25)
- `real scaled_inv_chi_square_cdf(reals y | reals nu, reals sigma)` - CDF (Available since 2.0)
- `real scaled_inv_chi_square_lcdf(reals y | reals nu, reals sigma)` - Log CDF (Available since 2.12)
- `real scaled_inv_chi_square_lccdf(reals y | reals nu, reals sigma)` - Log complementary CDF (Available since 2.12)
- `R scaled_inv_chi_square_rng(reals nu, reals sigma)` - Random variate generation (Available since 2.18)

## Exponential Distribution

### Probability Density Function

For rate parameter beta in R+, with y in R+:

Exponential(y|beta) = beta * exp(-beta*y)

### Distribution Statement

`y ~ exponential(beta)` - Available since 2.0

### Stan Functions

- `real exponential_lpdf(reals y | reals beta)` - Log density (Available since 2.12)
- `real exponential_lupdf(reals y | reals beta)` - Log density dropping constants (Available since 2.25)
- `real exponential_cdf(reals y | reals beta)` - CDF (Available since 2.0)
- `real exponential_lcdf(reals y | reals beta)` - Log CDF (Available since 2.12)
- `real exponential_lccdf(reals y | reals beta)` - Log complementary CDF (Available since 2.12)
- `R exponential_rng(reals beta)` - Random variate generation (Available since 2.18)

## Gamma Distribution

### Probability Density Function

For shape parameter alpha in R+ and rate parameter beta in R+, with y in R+:

Gamma(y|alpha,beta) = (beta^alpha / Gamma(alpha)) * y^(alpha - 1) * exp(-beta*y)

Mean: E[y] = alpha/beta; Variance: var[y] = alpha/beta^2

### Distribution Statement

`y ~ gamma(alpha, beta)` - Available since 2.0

### Stan Functions

- `real gamma_lpdf(reals y | reals alpha, reals beta)` - Log density (Available since 2.12)
- `real gamma_lupdf(reals y | reals alpha, reals beta)` - Log density dropping constants (Available since 2.25)
- `real gamma_cdf(reals y | reals alpha, reals beta)` - CDF (Available since 2.0)
- `real gamma_lcdf(reals y | reals alpha, reals beta)` - Log CDF (Available since 2.12)
- `real gamma_lccdf(reals y | reals alpha, reals beta)` - Log complementary CDF (Available since 2.12)
- `R gamma_rng(reals alpha, reals beta)` - Random variate generation (Available since 2.18)

## Inverse Gamma Distribution

### Probability Density Function

For parameters alpha in R+ and beta in R+, with y in R+:

InvGamma(y|alpha,beta) = (beta^alpha / Gamma(alpha)) * y^(-(alpha + 1)) * exp(-beta/y)

### Distribution Statement

`y ~ inv_gamma(alpha, beta)` - Available since 2.0

### Stan Functions

- `real inv_gamma_lpdf(reals y | reals alpha, reals beta)` - Log density (Available since 2.12)
- `real inv_gamma_lupdf(reals y | reals alpha, reals beta)` - Log density dropping constants (Available since 2.25)
- `real inv_gamma_cdf(reals y | reals alpha, reals beta)` - CDF (Available since 2.0)
- `real inv_gamma_lcdf(reals y | reals alpha, reals beta)` - Log CDF (Available since 2.12)
- `real inv_gamma_lccdf(reals y | reals alpha, reals beta)` - Log complementary CDF (Available since 2.12)
- `R inv_gamma_rng(reals alpha, reals beta)` - Random variate generation (Available since 2.18)

## Weibull Distribution

### Probability Density Function

For parameters alpha in R+ and sigma in R+, with y in [0,inf):

Weibull(y|alpha,sigma) = (alpha/sigma) * (y/sigma)^(alpha - 1) * exp(-(y/sigma)^alpha)

Note: If Y ~ Weibull(alpha,sigma), then Y^(-1) ~ Frechet(alpha,sigma^(-1))

### Distribution Statement

`y ~ weibull(alpha, sigma)` - Available since 2.0

### Stan Functions

- `real weibull_lpdf(reals y | reals alpha, reals sigma)` - Log density (Available since 2.12)
- `real weibull_lupdf(reals y | reals alpha, reals sigma)` - Log density dropping constants (Available since 2.25)
- `real weibull_cdf(reals y | reals alpha, reals sigma)` - CDF (Available since 2.0)
- `real weibull_lcdf(reals y | reals alpha, reals sigma)` - Log CDF (Available since 2.12)
- `real weibull_lccdf(reals y | reals alpha, reals sigma)` - Log complementary CDF (Available since 2.12)
- `R weibull_rng(reals alpha, reals sigma)` - Random variate generation (Available since 2.18)

## Frechet Distribution

### Probability Density Function

For parameters alpha in R+ and sigma in R+, with y in R+:

Frechet(y|alpha,sigma) = (alpha/sigma) * (y/sigma)^(-alpha - 1) * exp(-(y/sigma)^(-alpha))

Note: If Y ~ Frechet(alpha,sigma), then Y^(-1) ~ Weibull(alpha,sigma^(-1))

### Distribution Statement

`y ~ frechet(alpha, sigma)` - Available since 2.5

### Stan Functions

- `real frechet_lpdf(reals y | reals alpha, reals sigma)` - Log density (Available since 2.12)
- `real frechet_lupdf(reals y | reals alpha, reals sigma)` - Log density dropping constants (Available since 2.25)
- `real frechet_cdf(reals y | reals alpha, reals sigma)` - CDF (Available since 2.5)
- `real frechet_lcdf(reals y | reals alpha, reals sigma)` - Log CDF (Available since 2.12)
- `real frechet_lccdf(reals y | reals alpha, reals sigma)` - Log complementary CDF (Available since 2.12)
- `R frechet_rng(reals alpha, reals sigma)` - Random variate generation (Available since 2.18)

## Rayleigh Distribution

### Probability Density Function

For parameter sigma in R+, with y in [0,inf):

Rayleigh(y|sigma) = (y/sigma^2) * exp(-y^2/(2*sigma^2))

### Distribution Statement

`y ~ rayleigh(sigma)` - Available since 2.0

### Stan Functions

- `real rayleigh_lpdf(reals y | reals sigma)` - Log density (Available since 2.12)
- `real rayleigh_lupdf(reals y | reals sigma)` - Log density dropping constants (Available since 2.25)
- `real rayleigh_cdf(real y | real sigma)` - CDF (Available since 2.0)
- `real rayleigh_lcdf(real y | real sigma)` - Log CDF (Available since 2.12)
- `real rayleigh_lccdf(real y | real sigma)` - Log complementary CDF (Available since 2.12)
- `R rayleigh_rng(reals sigma)` - Random variate generation (Available since 2.18)

## Log-Logistic Distribution

### Probability Density Function

For parameters alpha, beta in R+, with y in R+:

LogLogistic(y|alpha,beta) = ((beta/alpha)*(y/alpha)^(beta-1)) / (1 + (y/alpha)^beta)^2

### Distribution Statement

`y ~ loglogistic(alpha, beta)` - Available since 2.29

### Stan Functions

- `real loglogistic_lpdf(reals y | reals alpha, reals beta)` - Log density (Available since 2.29)
- `real loglogistic_cdf(reals y | reals alpha, reals beta)` - CDF (Available since 2.29)
- `R loglogistic_rng(reals alpha, reals beta)` - Random variate generation (Available since 2.29)

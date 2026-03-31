# Multivariate Discrete Distributions

This Stan Functions Reference page documents probability distributions for multiple integer-valued outcomes, expressed as arrays.

## Multinomial Distribution

### Probability Mass Function

For K categories, N total count, and theta on a K-simplex, the PMF is:

Multinomial(y|theta) = (N choose y_1,...,y_K) prod_k theta_k^(y_k) where the multinomial coefficient equals N! / prod_k y_k!

### Distribution Statement

- `y ~ multinomial(theta)` increments target log probability with `multinomial_lupmf(y | theta)` (Available since 2.0)

### Stan Functions

- `real multinomial_lpmf(array[] int y | vector theta)` - log PMF with outcome array y and K-simplex parameter theta (Available since 2.12)
- `real multinomial_lupmf(array[] int y | vector theta)` - log PMF dropping constant terms (Available since 2.25)
- `array[] int multinomial_rng(vector theta, int N)` - generates multinomial variate (Available since 2.8)

## Multinomial Distribution, Logit Parameterization

### Probability Mass Function

Using unconstrained logistic scale: MultinomialLogit(y|gamma) = Multinomial(y|softmax(gamma))

### Distribution Statement

- `y ~ multinomial_logit(gamma)` increments target log probability with `multinomial_logit_lupmf(y | gamma)` (Available since 2.24)

### Stan Functions

- `real multinomial_logit_lpmf(array[] int y | vector gamma)` - log PMF with log K-simplex parameter gamma (Available since 2.24)
- `real multinomial_logit_lupmf(array[] int y | vector gamma)` - log PMF dropping constants (Available since 2.25)
- `array[] int multinomial_logit_rng(vector gamma, int N)` - generates variate with probabilities softmax(gamma) (Available since 2.24)

## Dirichlet-Multinomial Distribution

An overdispersed multinomial that generalizes Beta-binomial to multiple categories.

### Probability Mass Function

DirMult(y|theta) = [Gamma(alpha_0)*Gamma(N+1) / Gamma(N+alpha_0)] prod_k [Gamma(y_k+alpha_k) / Gamma(alpha_k)*Gamma(y_k+1)] where alpha_0 = sum_k alpha_k

### Distribution Statement

- `y ~ dirichlet_multinomial(alpha)` increments target log probability with `dirichlet_multinomial_lupmf(y | alpha)` (Available since 2.34)

### Stan Functions

- `real dirichlet_multinomial_lpmf(array[] int y | vector alpha)` - log PMF with positive K-vector parameter alpha (Available since 2.34)
- `real dirichlet_multinomial_lupmf(array[] int y | vector alpha)` - log PMF dropping constants (Available since 2.34)
- `array[] int dirichlet_multinomial_rng(vector alpha, int N)` - generates variate; equivalent to `multinomial_rng(dirichlet_rng(alpha), N)` (Available since 2.34)

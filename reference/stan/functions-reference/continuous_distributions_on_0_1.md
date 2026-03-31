# Continuous Distributions on [0, 1]

## Overview

"The continuous distributions with outcomes in the interval [0,1] are used to characterized bounded quantities, including probabilities."

## Beta Distribution

### Probability Density Function

For alpha in R+ and beta in R+, with theta in (0,1):

Beta(theta|alpha,beta) = (1/B(alpha,beta)) * theta^(alpha-1) * (1-theta)^(beta-1)

where B() is the beta function from combinatorial functions.

**Warning:** "If theta = 0 or theta = 1, then the probability is 0 and the log probability is -inf. Similarly, the distribution requires strictly positive parameters, alpha, beta > 0."

### Distribution Statement

```
theta ~ beta(alpha, beta)
```

Available since 2.0

### Stan Functions

- `real beta_lpdf(reals theta | reals alpha, reals beta)` - Log of the beta density of theta in [0,1] given positive prior successes (plus one) alpha and prior failures (plus one) beta. Available since 2.12
- `real beta_lupdf(reals theta | reals alpha, reals beta)` - Log of the beta density dropping constant additive terms. Available since 2.25
- `real beta_cdf(reals theta | reals alpha, reals beta)` - Beta cumulative distribution function. Available since 2.0
- `real beta_lcdf(reals theta | reals alpha, reals beta)` - Log of the beta CDF. Available since 2.12
- `real beta_lccdf(reals theta | reals alpha, reals beta)` - Log of the beta complementary CDF. Available since 2.12
- `R beta_rng(reals alpha, reals beta)` - Generate a beta variate. Available since 2.18

## Beta Proportion Distribution

### Probability Density Function

For mu in (0, 1) and kappa in R+, with theta in (0,1):

Beta_Proportion(theta|mu,kappa) = (1/B(mu*kappa, (1-mu)*kappa)) * theta^(mu*kappa-1) * (1-theta)^((1-mu)*kappa-1)

**Warning:** "If theta = 0 or theta = 1, then the probability is 0 and the log probability is -inf. Similarly, the distribution requires mu in (0, 1) and strictly positive parameter, kappa > 0."

### Distribution Statement

```
theta ~ beta_proportion(mu, kappa)
```

Available since 2.19

### Stan Functions

- `real beta_proportion_lpdf(reals theta | reals mu, reals kappa)` - Log of the beta_proportion density given mean mu and precision kappa. Available since 2.19
- `real beta_proportion_lupdf(reals theta | reals mu, reals kappa)` - Log of the beta_proportion density dropping constant additive terms. Available since 2.25
- `real beta_proportion_lcdf(reals theta | reals mu, reals kappa)` - Log of the beta_proportion CDF. Available since 2.18
- `real beta_proportion_lccdf(reals theta | reals mu, reals kappa)` - Log of the beta_proportion complementary CDF. Available since 2.18
- `R beta_proportion_rng(reals mu, reals kappa)` - Generate a beta_proportion variate. Available since 2.18

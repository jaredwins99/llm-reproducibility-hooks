# Bounded Continuous Distributions

## Overview

The bounded continuous distributions have support on a finite interval of real numbers.

## Uniform Distribution

### Probability Density Function

For alpha in R and beta in (alpha, inf), where y in [alpha, beta]:

Uniform(y | alpha, beta) = 1 / (beta - alpha)

### Distribution Statement

```stan
y ~ uniform(alpha, beta)
```

Increments target log probability density with `uniform_lupdf(y | alpha, beta)`.

*Available since 2.0*

### Stan Functions

**`real uniform_lpdf(reals y | reals alpha, reals beta)`**
- Computes the logarithm of the uniform density
- *Available since 2.12*

**`real uniform_lupdf(reals y | reals alpha, reals beta)`**
- Logarithm of uniform density excluding constant additive terms
- *Available since 2.25*

**`real uniform_cdf(reals y | reals alpha, reals beta)`**
- The cumulative distribution function
- *Available since 2.0*

**`real uniform_lcdf(reals y | reals alpha, reals beta)`**
- Logarithm of the cumulative distribution function
- *Available since 2.12*

**`real uniform_lccdf(reals y | reals alpha, reals beta)`**
- Logarithm of the complementary cumulative distribution function
- *Available since 2.12*

**`R uniform_rng(reals alpha, reals beta)`**
- Generates uniform variates; available only in transformed data and generated quantities blocks
- *Available since 2.18*

# Binary Distributions - Stan Functions Reference

## Overview

"Binary probability distributions have support on {0,1}, where 1 represents the value true and 0 the value false."

## Bernoulli Distribution

### Probability Mass Function

The Bernoulli distribution with parameter theta in [0,1] for y in {0,1} is defined as:
- theta if y = 1
- 1 - theta if y = 0

### Distribution Statement

```
y ~ bernoulli(theta)
```

Increments target log probability density with `bernoulli_lupmf(y | theta)`. Available since 2.0.

### Stan Functions

**Log Probability Mass Functions:**
- `real bernoulli_lpmf(ints y | reals theta)` — Log Bernoulli probability mass (Available since 2.12)
- `real bernoulli_lupmf(ints y | reals theta)` — Log probability dropping constant terms (Available since 2.25)

**Cumulative Distribution Functions:**
- `real bernoulli_cdf(ints y | reals theta)` — CDF (Available since 2.0)
- `real bernoulli_lcdf(ints y | reals theta)` — Log CDF (Available since 2.12)
- `real bernoulli_lccdf(ints y | reals theta)` — Log complementary CDF (Available since 2.12)

**Random Number Generation:**
- `ints bernoulli_rng(reals theta)` — Generate Bernoulli variates (Available since 2.18)

---

## Bernoulli Distribution, Logit Parameterization

This parameterization provides "more numerical stability if the chance-of-success parameter is on the logit scale."

### Probability Mass Function

For alpha in R and y in {0,1}:
- logit^{-1}(alpha) if y = 1
- 1 - logit^{-1}(alpha) if y = 0

### Distribution Statement

```
y ~ bernoulli_logit(alpha)
```

Increments target with `bernoulli_logit_lupmf(y | alpha)`. Available since 2.0.

### Stan Functions

**Log Probability Mass Functions:**
- `real bernoulli_logit_lpmf(ints y | reals alpha)` — Log probability with inv_logit(alpha) (Available since 2.12)
- `real bernoulli_logit_lupmf(ints y | reals alpha)` — Log probability dropping constants (Available since 2.25)

**Random Number Generation:**
- `R bernoulli_logit_rng(reals alpha)` — Generate Bernoulli variates (Available since 2.18)

---

## Bernoulli-Logit Generalized Linear Model (Logistic Regression)

"A function for a logistic regression" providing "more efficient implementation than manually written regression."

### Probability Mass Function

For x in R^{n x m}, alpha in R^n, beta in R^m, and y in {0,1}^n:

Product of Bernoulli terms with success probability logit^{-1}(alpha_i + x_i * beta)

### Distribution Statement

```
y ~ bernoulli_logit_glm(x, alpha, beta)
```

Increments target with `bernoulli_logit_glm_lupmf(y | x, alpha, beta)`. Available since 2.25.

### Stan Functions

**Multiple Signatures for Log Probability:**

With scalar alpha:
- `real bernoulli_logit_glm_lpmf(int y | matrix x, real alpha, vector beta)` (2.23+)
- `real bernoulli_logit_glm_lupmf(int y | matrix x, real alpha, vector beta)` (2.25+)
- `real bernoulli_logit_glm_lpmf(array[] int y | row_vector x, real alpha, vector beta)` (2.23+)
- `real bernoulli_logit_glm_lupmf(array[] int y | row_vector x, real alpha, vector beta)` (2.25+)
- `real bernoulli_logit_glm_lpmf(array[] int y | matrix x, real alpha, vector beta)` (2.18+)
- `real bernoulli_logit_glm_lupmf(array[] int y | matrix x, real alpha, vector beta)` (2.25+)

With vector alpha:
- `real bernoulli_logit_glm_lpmf(int y | matrix x, vector alpha, vector beta)` (2.23+)
- `real bernoulli_logit_glm_lupmf(int y | matrix x, vector alpha, vector beta)` (2.25+)
- `real bernoulli_logit_glm_lpmf(array[] int y | row_vector x, vector alpha, vector beta)` (2.23+)
- `real bernoulli_logit_glm_lupmf(array[] int y | row_vector x, vector alpha, vector beta)` (2.25+)
- `real bernoulli_logit_glm_lpmf(array[] int y | matrix x, vector alpha, vector beta)` (2.18+)
- `real bernoulli_logit_glm_lupmf(array[] int y | matrix x, vector alpha, vector beta)` (2.25+)

**Random Number Generation:**
- `array[] int bernoulli_logit_glm_rng(matrix x, vector alpha, vector beta)` (2.29+)
- `array[] int bernoulli_logit_glm_rng(row_vector x, vector alpha, vector beta)` (2.29+)

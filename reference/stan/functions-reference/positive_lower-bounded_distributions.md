# Positive Lower-Bounded Distributions

This documentation covers Stan probability distributions with support on values above a positive minimum. Three main distributions are documented:

## Pareto Distribution

**Probability Density Function:**
The Pareto distribution for y >= y_min is defined as:
Pareto(y|y_min,alpha) = (alpha * y_min^alpha) / y^(alpha+1)

**Distribution Statement:**
`y ~ pareto(y_min, alpha)`

**Available Functions:**
- `pareto_lpdf(reals y | reals y_min, reals alpha)` - log probability density
- `pareto_lupdf(reals y | reals y_min, reals alpha)` - log density (dropping constants)
- `pareto_cdf(reals y | reals y_min, reals alpha)` - cumulative distribution
- `pareto_lcdf(reals y | reals y_min, reals alpha)` - log of CDF
- `pareto_lccdf(reals y | reals y_min, reals alpha)` - log complementary CDF
- `pareto_rng(reals y_min, reals alpha)` - random variate generation

## Pareto Type 2 Distribution

**Probability Density Function:**
For y >= mu: Pareto_Type_2(y|mu,lambda,alpha) = (alpha/lambda) * (1 + (y-mu)/lambda)^(-(alpha+1))

The Lomax distribution is a special case where mu=0.

**Distribution Statement:**
`y ~ pareto_type_2(mu, lambda, alpha)`

**Available Functions:**
- `pareto_type_2_lpdf(reals y | reals mu, reals lambda, reals alpha)` - log density
- `pareto_type_2_lupdf(reals y | reals mu, reals lambda, reals alpha)` - log density (constants dropped)
- `pareto_type_2_cdf(reals y | reals mu, reals lambda, reals alpha)` - CDF
- `pareto_type_2_lcdf`, `pareto_type_2_lccdf` - log variants
- `pareto_type_2_rng(reals mu, reals lambda, reals alpha)` - random generation

## Wiener First Passage Time Distribution

This represents the first passage time in a diffusion process with multiple variations supporting inter-trial variability.

**Core Parameters:**
- alpha: boundary separation
- tau: non-decision time
- beta: starting point (0 < beta < 1)
- delta: drift rate

**Extended Parameters (versions 2.35+):**
- var_delta: inter-trial drift variability
- var_beta: starting point variability
- var_tau: non-decision time variability

**Distribution Statements:**
```
y ~ wiener(alpha, tau, beta, delta)
y ~ wiener(alpha, tau, beta, delta, var_delta)
y ~ wiener(alpha, tau, beta, delta, var_delta, var_beta, var_tau)
```

**Available Functions:**
- `wiener_lpdf` - log probability density (multiple signatures)
- `wiener_lupdf` - log density (constants dropped)
- `wiener_lcdf_unnorm(real y, real alpha, real tau, real beta, real delta)` - unnormalized log CDF
- `wiener_lccdf_unnorm` - unnormalized log complementary CDF

**Important Notes:**
The CDF and complementary CDF functions are conditional and unnormalized, asymptoting at the probability of hitting the upper boundary rather than 1.

**Lower Boundary:** To compute results for the lower boundary, use Wiener(y | alpha, tau, 1-beta, -delta)

**Tolerance Tuning:** The 5- and 7-argument forms accept an additional `data real` argument for precision control (defaults: 1e-4 for density, 1e-8 for CDF functions).

# Proportionality Constants in Stan

## Overview

The Stan documentation explains that when computing log densities for MCMC, variational inference, or optimization, you often only need to evaluate functions "up to a proportionality constant (or similarly compute log densities up to an additive constant)." This efficiency comes from the fact that normalized distributions aren't strictly required for sampling or inference.

## Three Density Computation Syntaxes

Stan provides three approaches:

1. **Unnormalized densities** (dropping proportionality constants):
   - Distribution statement: `x ~ normal(0, 1);`
   - Log density increment: `target += normal_lupdf(x | 0, 1);`

2. **Normalized densities** (keeping all constants):
   - `target += normal_lpdf(x | 0, 1);`

3. **Discrete distributions** use `_lupmf` and `_lpmf` variants similarly.

## Mathematical Basis

When a density p(θ) factors as K·g(θ), where K contains non-θ terms and g(θ) contains θ-dependent terms, the function g is proportional to p. For the normal distribution, the full log density is:

`normal_lpdf(x | μ, σ) = -log(σ√(2π)) - ½((x-μ)/σ)²`

The unnormalized version drops the constant term: `-½((x-μ)/σ)²`

## Key Recommendations

Use normalized functions (`_lpdf`/`_lpmf`) when "proportionality constants were needed" for accuracy. Only employ unnormalized versions when "it is absolutely clear that the proportionality constants are not necessary."

## Custom Distributions

When defining custom probability functions, the compiler "automatically make available a `_lupdf` or `_lupmf` version" based on the normalized `_lpdf` or `_lpmf` definition. These functions can only be used in model blocks or within other probability functions.

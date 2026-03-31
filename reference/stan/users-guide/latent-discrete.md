# Latent Discrete Parameters in Stan

## Overview

Stan cannot directly sample discrete parameters, but many models with bounded discrete parameters can be implemented through marginalization. This approach involves algebraically integrating out discrete parameters from the joint probability function.

## Key Benefits of Marginalization

A significant advantage is obtaining the posterior expectation of marginalized variables—often the quantity of interest. This enables better exploration of distribution tails and more efficient sampling since expectations across all possible values are utilized rather than relying on discrete parameter sampling alone.

## Change Point Models

### Basic Model Structure

The coal mining disasters example (1851–1962) demonstrates a Poisson model with two rate parameters that change at an unknown time point *s*:

- *e* ~ exponential(r_e) [early rate]
- *l* ~ exponential(r_l) [late rate]
- *s* ~ uniform(1, T) [change point]
- D_t ~ Poisson(t < s ? e : l) [disaster count]

### Marginalization Mathematics

The joint probability factors as:
- p(e,l,s,D) = p(e) p(l) p(s) p(D|s,e,l)

To marginalize *s*, we compute:
- p(D|e,l) = Σ_s p(s) p(D|s,e,l)

On the log scale (required for Stan):
- log p(D|e,l) = log_sum_exp over s of [log uniform(s|1,T) + Σ_t log Poisson(D_t|...)]

### Stan Implementation

The code uses `log_sum_exp` for numerical stability. A key optimization reduces the quadratic complexity (O(T²)) to linear (O(T)) through dynamic programming, achieving approximately 20x speedup on real datasets.

## Mark-Recapture Models

### Lincoln-Petersen Estimator

For simple mark-recapture studies with *M* marked animals and *R* recaptured in a second sample of *C*:

- Population estimate: N̂ = MC/R
- Probabilistic model: R ~ binomial(C, M/N)

### Cormack-Jolly-Seber Model

This open-population model accommodates mortality using:
- φ_t: survival probability from time t to t+1
- p_t: capture probability at time t
- z_{i,t}: latent indicator of whether individual *i* is alive at time *t*

The key derived quantity χ_t represents the probability an animal is never recaptured if alive at time *t*:

- χ_t = 1 if t = T
- χ_t = (1 - φ_t) + φ_t(1 - p_{t+1})χ_{t+1} if t < T

This recursive definition allows marginalization without explicit discrete parameters.

## Data Coding and Diagnostic Accuracy

### Dawid-Skene Model

This framework handles categorical ratings by coders/diagnostic tests with discrete true categories *z_i* marginalized out:

- z_i ~ categorical(π) [true category]
- y_{i,j} ~ categorical(θ_{j,z_i}) [rater j's rating for item i]

Parameters:
- π: prevalence of categories
- θ_{j,k}: response patterns of rater j to true category k

The likelihood marginalizing *z* becomes:
- log p(y|θ,π) = Σ_i log(Σ_k exp[log categorical(k|π) + Σ_j log categorical(y_{i,j}|θ_{j,k})])

This directly implements the E-step of the EM algorithm used in the original paper.

## Recovering Marginalized Parameters

### Mathematical Framework

When both continuous (Θ) and discrete (Z) parameters exist, estimates of E[g(Θ,Z)] use the law of iterated expectation:

- E[g(Θ,Z)] = E[E[g(Θ,Z)|Θ]]

For each MCMC draw θ^(i), compute: h(θ^(i)) = Σ_k g(θ^(i),k)Pr[Z=k|Θ=θ^(i)]

### Special Cases

When g depends only on Θ: standard estimation applies (marginalization has no effect on continuous parameter expectations)

When g depends only on Z: compute h(Θ) = Σ_k g(k)Pr[Z=k|Θ]

For posterior probabilities of discrete parameters:
- Pr[Z=k|Y] ≈ (1/M)Σ_i Pr[Z=k|Θ=θ^(i), Y]

This can be computed via Bayes' theorem using conditional likelihoods and prior probabilities.

## Computational Considerations

- **Quadratic models**: feasible for reasonable problem sizes
- **Multiple change points**: complexity increases polynomially (quadratic for two points, cubic for three)
- **Identifiability**: some parameters may be unidentified (e.g., final survival and capture probabilities in CJS)—use derived quantities for identified combinations

Stan's approach efficiently handles these marginalized models without requiring discrete sampling, enabling better posterior exploration and more stable convergence than Gibbs-sampling alternatives.

# Posterior Analysis - Stan Reference Manual

## Overview

Stan employs Markov chain Monte Carlo (MCMC) techniques to generate posterior distribution draws for Bayesian inference. The document explains convergence diagnostics, effective sample size estimation, and related computational considerations for analyzing MCMC output.

## Key Concepts

### Markov Chains
A Markov chain is "a sequence of random variables where each variable is conditionally independent of all other variables given the value of the previous value." Stan uses Hamiltonian Monte Carlo to generate chain states, producing ergodic and stationary chains that reach an equilibrium distribution matching the target posterior density.

### Convergence Monitoring

**Potential Scale Reduction (R-hat):** This statistic compares within-chain variance to pooled cross-chain variance. Values near 1.0 indicate convergence, with Vehtari et al. recommending a threshold of 1.01. The calculation uses between-chain variance (B) and within-chain variance (W):

- Between-chain variance measures spread of chain means
- Within-chain variance averages individual chain variances
- The estimator combines these: var_hat+(theta|y) = (N-1)/N * W + 1/N * B
- R-hat = sqrt[var_hat+(theta|y) / W]

**Split R-hat:** Each chain is bisected before computing R-hat to detect gradual drift within individual chains that might escape detection otherwise.

**Rank Normalization:** To handle heavy-tailed posteriors, values are rank-transformed and converted to normal scores using inverse normal transformation. Folded R-hat examines absolute deviations from the median for tail behavior assessment.

### Effective Sample Size (ESS)

MCMC draws exhibit autocorrelation, reducing statistical efficiency compared to independent samples. ESS adjusts for this correlation:

N_eff = N / (1 + 2 * sum(rho_t))

where rho_t represents autocorrelation at lag t. Stan estimates autocorrelations via FFT and combines cross-chain variance estimates with within-chain calculations. The document notes that "anticorrelated draws" can produce N_eff exceeding N, making MCMC superior to independent sampling for certain problems.

### MCMC Standard Error

Monte Carlo standard error (MCSE) is estimated as posterior standard deviation divided by sqrt(N_eff). This reflects estimation uncertainty for posterior quantities.

### Thinning

The guide clarifies that "the only reason to thin a sample is to reduce memory requirements." While thinning can reduce autocorrelation in positively correlated sequences, unthinned chains typically yield higher effective sample sizes. Thinning anticorrelated sequences worsens efficiency.

## Convergence Is Global

Convergence assessment should include all parameters and log-posterior density (lp__), as convergence is a property of the entire chain composition, not individual functions. The Cramer-Wold theorem ensures multivariate convergence when all margins converge.

## References

The document cites foundational works by Gelman & Rubin (1992), Geyer (1992, 2011), Metropolis et al. (1953), and recent improvements by Vehtari et al. (2021).

# Simulation-Based Calibration

## Overview

Simulation-based calibration (SBC) is a methodology for validating Bayesian posterior samplers by testing whether posterior intervals achieve appropriate coverage. The approach exploits a fundamental property: when data is generated from a model, Bayesian inference with respect to that model produces calibrated posteriors by construction.

## Core Principle: Calibration by Construction

The calibration property emerges from Bayesian theory. When parameters are simulated from a prior p(θ) and data from the sampling density p(y|θ), the resulting (y, θ) pairs follow the joint distribution p(y,θ). Since the simulated parameters are distributed according to the posterior p(θ|y^sim), the rank statistics of simulated parameters relative to posterior draws should be uniformly distributed.

This uniformity guarantees that posterior intervals contain true parameter values at their nominal rates. For example, 90% credible intervals will contain the true value approximately 90% of the time.

## SBC Methodology

The process involves:

1. **Simulation**: Generate N independent (y^sim(n), θ^sim(n)) pairs from the joint distribution
2. **Posterior inference**: For each simulated dataset, draw M posterior samples
3. **Rank calculation**: For each parameter k and simulation n, compute the rank r(n,k) as the count of posterior draws less than the simulated value
4. **Uniformity testing**: Assess whether ranks follow a uniform distribution from 0 to M

The rank formula is:

r(n,k) = Σ I[θ_k^(n,m) < θ_k^sim(n)]

If the algorithm performs correctly, ranks should follow a categorical distribution with equal probability 1/(M+1) across all possible values.

## Implementation in Stan

Stan programs can incorporate SBC testing through a three-block structure:

**Transformed Data Block**: Generates parameters and data using random number generators
**Parameters and Model Blocks**: Specify the model conditioned on simulated data
**Generated Quantities Block**: Records comparison indicators (whether each parameter is less than its simulated value)

A simple example for a normal model:

```stan
transformed data {
  real mu_sim = normal_rng(0, 1);
  real<lower=0> sigma_sim = lognormal_rng(0, 1);
  int J = 10;
  vector[J] y_sim;
  for (j in 1:J) {
    y_sim[j] = normal_rng(mu_sim, sigma_sim);
  }
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  mu ~ normal(0, 1);
  sigma ~ lognormal(0, 1);
  y_sim ~ normal(mu, sigma);
}
generated quantities {
  array[2] int<lower=0, upper=1> lt_sim
      = { mu < mu_sim, sigma < sigma_sim };
}
```

## Testing Uniformity

A chi-squared test assesses rank uniformity by binning ranks into J categories. The test statistic is:

X² = Σ (b_j - e_j)² / e_j

where b_j is observed counts and e_j is expected counts per bin. Under uniformity, X² follows a chi-squared distribution with J-1 degrees of freedom.

For computational efficiency, if M+1 is divisible by J, ranks can be binned using:

bin(r,M,J) = 1 + ⌊r·J/(M+1)⌋

## Critical Implementation Details

**Thinning**: Posterior draws should be thinned to near-independence to avoid spurious uniformity violations. The effective sample size should approximate the number of retained draws.

**Duplication**: Implementing the data-generating process twice (in transformed data and in the model) reduces coding errors, though it increases effort.

**Indexing precision**: Off-by-one errors in binning are common; careful attention to boundaries prevents artifacts in uniformity assessment.

## Examples of Outcomes

### Correct Specification
When a model matches its data-generating process (normal model with normal data), rank histograms appear uniformly distributed across all bins, confirming proper calibration.

### Misspecification
Using a normal model with Student-t generated data shows non-uniform ranks, particularly for scale parameters. Simulated values tend to be much smaller than fitted values, clearly indicating calibration failure.

### Sampler Failure
Even with correct model specification, difficult posterior geometry can cause sampler failure. The eight-schools hierarchical meta-analysis model demonstrates this problem: while population parameters appear calibrated, school-specific effects show severe non-uniformity due to extreme curvature near the boundary where the between-school variance approaches zero.

## Key References

The methodology builds on Cook, Gelman, and Rubin (2006) and was refined by Talts et al. (2018), who emphasize visual inspection of binned rank plots alongside formal hypothesis testing.

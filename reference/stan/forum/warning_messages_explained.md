# Stan Warning Messages: Understanding and Responding

Source: https://discourse.mc-stan.org/t/text-for-warning-message/16928

## Divergent Transitions Warning

**Message**: "There were X divergent transitions after warmup."

**What it means**: The sampler encountered regions of the posterior where the geometry
is too difficult to explore accurately. Even a small number of divergences cannot be
safely ignored -- they almost always signal a real problem.

**What NOT to do**: Do not simply increase `adapt_delta` to 0.999 and report results.
This is a computational band-aid that slows execution without solving the underlying
modeling problem.

**What TO do**:
1. Check for coding errors and missing priors
2. Examine pairs plots for funnel shapes or clustering at extreme values
3. Consider reparameterization (non-centered for hierarchical models)
4. Add informative priors where appropriate
5. Only adjust `adapt_delta` after structural improvements

## Key Debate: Statistical Rigor vs. Practical Guidance

The Stan community debated how warning messages should be worded:

- **Andrew Gelman**: Warnings should encourage better statistical practices. Suggesting
  "using a stronger prior may help" points toward regularization rather than
  computational tweaking.

- **Ben Goodrich**: Without constructive guidance, users simply report results with
  unresolved divergent transitions. Divergences often stem from identifiability issues
  beyond user control (especially in packages like rstanarm or brms).

## Current Recommended Warning

> "There were [X] divergent transitions after warmup, which may compromise the
> validity of the estimates. See [documentation link] to find why this is a potential
> problem and how to remove them."

This approach emphasizes severity while directing users to comprehensive resources
rather than suggesting a single computational fix.

## Other Common Warnings

### Maximum Treedepth Exceeded
The sampler needed more leapfrog steps than allowed. Usually indicates strong
posterior correlations. Fix: reparameterize to reduce correlations.

### Low E-BFMI (Bayesian Fraction of Missing Information)
The sampler had difficulty exploring the posterior. Often caused by heavy-tailed
posteriors or multimodality. Fix: more informative priors, reparameterization.

### Large Rhat Values (> 1.01)
Chains have not converged. Run longer chains, check for multimodality, or fix
model specification issues.

### Low Effective Sample Size
The chains are highly autocorrelated. Indicates inefficient sampling due to
posterior geometry. Fix: reparameterize, add priors.

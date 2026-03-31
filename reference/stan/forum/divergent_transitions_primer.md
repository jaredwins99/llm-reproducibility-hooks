# Divergent Transitions in Stan: A Primer

Source: https://discourse.mc-stan.org/t/divergent-transitions-a-primer/17099

## What Are Divergent Transitions?

Divergent transitions are warnings that indicate problems with the posterior geometry
when using Stan's NUTS sampler. The intuitive analogy: "imagine walking down a steep
mountain. If you take too big of a step you will fall, so you need to take it slow."
The posterior distribution's uneven or degenerate geometry prevents the sampler from
finding an appropriate step size for efficient exploration.

## 13 Diagnostic and Resolution Approaches

### 1. Code Review
Check for programming errors: missing priors, incorrect array indexing, improper
parameter bounds.

### 2. Simulation Testing
Create a simulated dataset with known true values of all parameters to verify the
model recovers true values correctly.

### 3. Model Reduction
Build minimal models first, progressively adding complexity only after resolving
issues.

### 4. Visualization
Use tools like `mcmc_parcoord`, Shinystan, and pairs plots to identify problematic
parameter spaces.

### 5. Identifiability Assessment
Check whether parameters are well-informed by data and whether multiple posterior
modes exist.

### 6. Prior Specification
Introduce more informative priors cautiously, avoiding prior bias while addressing
degeneracy.

### 7. Prior-Posterior Comparison
Examine whether posterior heavily concentrates in prior tails or on boundaries.

### 8. Reparameterization
Transform parameters to be independent, informed by data and without sharp
irregularities.

### 9. Sequential Parameter Testing
Move parameters from data to parameters block one at a time.

### 10. Tight Prior Testing
Test tight priors centered on true values to isolate problem parameters.

### 11. Optimization Mode
Run `optimizing` mode for validation.

### 12. Gradient Testing
Execute `test_grad` diagnostics.

### 13. Sampler Settings (Last Resort)
Adjust `adapt_delta` and `max_treedepth` only after structural improvements.

## Key Caution

This is not a definitive checklist but rather "a map" for exploration. Success
requires understanding underlying statistical concepts rather than mechanical
application of techniques.

## Important Resources

- Mike Betancourt's Identity Crisis case study
- Principled Bayesian Workflow materials
- Hierarchical modeling resources
- bayesplot package visualization guidance

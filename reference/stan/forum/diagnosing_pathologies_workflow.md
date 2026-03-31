# Identifying Pathologies from Divergent Transitions: Step-by-Step Workflow

Source: https://discourse.mc-stan.org/t/best-way-to-identify-pathologies-from-divergent-transitions-general-step-by-step-workflow/4358

## Core Concept

Divergences occur when simulated Hamiltonian dynamics deviates from the true
posterior path, typically caused by strong curvature in the unconstrained parameter
space. Divergent samples tend to be reported outside of the problematic region,
somewhere before the geometry starts to be difficult.

## Step-by-Step Diagnostic Workflow

### 1. Visual Inspection with Pairs Plots
Start by examining bivariate relationships in ShinyStan or using `pairs()`:
- **Funnel shapes** suggest hierarchical model issues
- **Extreme value clustering** (around e^+/-15) indicates numeric stability problems

### 2. Parallel Coordinate Plots
Use the `bayesplot` package's `mcmc_parcoord()` function to visualize all parameters
simultaneously, highlighting which ones concentrate around problematic values during
divergences.

### 3. Focused Parameter Analysis
For models with numerous parameters, focus on "local" parameters against shared
scale parameters. Plot one or a handful of local parameters against a scale parameter
that they all share a dependency on.

### 4. Traceplot Examination
Look for parameters that appear "stuck" for multiple iterations, suggesting
convergence issues.

## Common Pathologies and Solutions

### Hierarchical Funnel Problem
Reparameterize to indirectly sample from the problematic region using the
non-centered parameterization.

### Positive Parameters
Instead of constraining then transforming, use log-space sampling:

```stan
// Avoid this pattern
real<lower=0> x;
x ~ gamma(a,b);

// Use log-space sampling instead
real x_log;
target += x_log; // Jacobian adjustment
target += a*log(b) - lgamma(a) + (a-1)*x_log - b*exp(x_log);
```

### Extreme Values
Apply tighter priors or maintain parameters in log-space to preserve numeric
stability.

## Semi-Automated Identification

A machine learning approach involves:
- Creating datasets with MCMC iterations as rows, parameters as columns
- Adding a binary divergence indicator column
- Training decision trees to identify which parameters predict divergences

This surfaces the variables and parts of the parameter space associated with
divergences.

## Key Resources

- Michael Betancourt's case studies on divergences
- Martin Modrak's blog posts on taming divergences
- bayesplot package vignette on visual diagnostics

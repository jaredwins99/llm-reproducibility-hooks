# Visual MCMC Diagnostics Using Bayesplot

Source: https://mc-stan.org/bayesplot/articles/visual-mcmc-diagnostics.html

Authored by Jonah Gabry and Martin Modrak. Documents diagnostic visualization tools for MCMC sampling.

## NUTS-Specific Diagnostics

Specialized functions for the No-U-Turn Sampler (NUTS), the HMC variant used by Stan:

- `mcmc_nuts_acceptance`
- `mcmc_nuts_divergence`
- `mcmc_nuts_energy`
- `mcmc_nuts_stepsize`
- `mcmc_nuts_treedepth`

These require additional information beyond posterior draws, including log-posterior density and NUTS-specific diagnostic values.

## Divergent Transitions

Multiple visualization approaches identify divergence problems:

**mcmc_parcoord**: Shows one line per iteration, connecting the parameter values at each iteration to reveal global divergence patterns.

**mcmc_pairs**: Displays univariate histograms and bivariate scatter plots, useful for identifying collinearity and non-identifiabilities.

**mcmc_scatter**: Examines single bivariate relationships closely, particularly effective for hierarchical models comparing local and global parameters.

**mcmc_trace**: Time series plots showing chain evolution, with optional divergence rugs.

**mcmc_nuts_divergence**: Compares log-posterior and acceptance statistics between divergent and non-divergent samples.

## Case Study: Eight Schools Example

Uses hierarchical meta-analysis of test-prep programs across eight schools to demonstrate centered versus non-centered parameterization:

- The **centered** approach exhibits "funnel" geometry causing divergences at small tau values
- The **non-centered** reparameterization avoids this problem

The non-centered parameterization substantially improves sampling efficiency, demonstrating how reparameterization is required when increasing adapt_delta alone cannot eliminate fundamental geometry problems.

## General MCMC Diagnostics

### Rhat (Potential Scale Reduction Statistic)

Compares within-chain and across-chain variance to assess convergence. Values should approach 1.0.

Visualization functions: `mcmc_rhat` and `mcmc_rhat_hist`.

### Effective Sample Size (n_eff)

Estimates independent draws accounting for autocorrelation. The ratio n_eff/N should ideally exceed 0.1.

Functions: `mcmc_neff` and `mcmc_neff_hist`.

### Autocorrelation

`mcmc_acf` and `mcmc_acf_bar` display correlations across lag distances, with emphasis on rapid decay to zero.

## Key Takeaway

Diagnostic visualization enables understanding "why the Markov chains are struggling" rather than simply identifying that problems exist.

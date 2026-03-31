# Bayesplot Function Reference

Source: https://mc-stan.org/bayesplot/reference/index.html

bayesplot package (version 1.15.0) -- Plotting for Bayesian Models. Developed by Jonah Gabry and Tristan Mahr.

## Main Function Categories

### Posterior Predictive Checking (PPC)

Extensive graphical model checking functions that compare observed data to posterior or prior predictive distributions. These cover:
- Discrete outcomes
- Distributions
- Errors
- Intervals
- Scatterplots
- Test statistics

### Posterior Predictive Distribution (PPD)

Similar visualization functions for displaying simulated data without observed data comparisons.

### MCMC Diagnostics

Comprehensive plotting tools for Markov chain Monte Carlo draws:
- Trace plots
- Density estimates
- Interval estimates
- Parameter recovery comparisons

### HMC/NUTS Diagnostics

Specialized functions for Hamiltonian Monte Carlo and No-U-Turn Sampler diagnostics:
- Acceptance rates
- Divergence
- Stepsize
- Tree depth
- Energy plots

### Aesthetics

Functions for customizing color schemes and themes throughout visualizations.

### Helper Functions

Tools for arranging plots, modifying ggplot elements, and parameter selection using tidy approaches.

### Data Extraction

Functions to extract diagnostic quantities like Rhat values and effective sample size ratios from fitted model objects.

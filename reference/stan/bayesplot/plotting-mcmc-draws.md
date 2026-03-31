# Plotting MCMC Draws Using Bayesplot

Source: https://mc-stan.org/bayesplot/articles/plotting-mcmc-draws.html

Vignette from bayesplot package (version 1.15.0), authored by Jonah Gabry. Focuses on visualizing Markov chain Monte Carlo (MCMC) posterior draws from Bayesian models.

## Introduction & Setup

The bayesplot package works alongside ggplot2 and rstanarm. Separate documentation exists for MCMC diagnostics and posterior predictive checking.

## Example Model

Functions are demonstrated using a linear regression fitted to the mtcars dataset via `stan_glm`, producing 1,000 iterations across 4 chains with 12 parameters (11 predictors plus sigma).

## Posterior Uncertainty Intervals

Two visualization approaches:

- **`mcmc_intervals`**: Shows central intervals with medians, defaulting to 50% inner and 90% outer bands
- **`mcmc_areas`**: Displays intervals as shaded density regions, allowing customization of probability levels and point estimates

## Univariate Marginal Posterior Distributions

Five functions visualize individual parameter distributions:

- **`mcmc_hist`**: Combined chain histograms
- **`mcmc_hist_by_chain`**: Separate histograms per chain in facets
- **`mcmc_dens`**: Kernel density estimates across chains
- **`mcmc_dens_overlay`**: Overlaid density curves for each chain
- **`mcmc_violin`**: Violin plots with quantile lines

All support the `transformations` argument for on-the-fly variable modifications.

## Bivariate Plots

Three functions examine joint distributions:

- **`mcmc_scatter`**: Simple two-parameter scatterplots
- **`mcmc_hex`**: Hexagonal binning to reduce overplotting
- **`mcmc_pairs`**: Multi-parameter pairs matrices with flexibility in diagonal and off-diagonal specifications

## Trace Plots

Time-series visualizations of chain sequences:

- **`mcmc_trace`**: Standard trace plots with color scheme options
- **`mcmc_trace_highlight`**: Points with selective opacity to emphasize individual chains

## Color Schemes

Multiple color schemes available: red, green, blue, brightblue, purple, teal, gray, pink, viridis, and mix-blue-red variants.

## Key Features

- Functions support parameter selection via `pars` argument
- Customizable intervals, quantiles, and point estimates
- Faceting and layout control through `facet_args`
- Optional transformations without pre-processing data

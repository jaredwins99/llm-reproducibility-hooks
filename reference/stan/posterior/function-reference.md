# Posterior Package Function Reference

Source: https://mc-stan.org/posterior/reference/index.html

posterior R package (version 1.6.0). Authors: Paul-Christian Burkner, Jonah Gabry, Matthew Kay, Aki Vehtari.

## Main Categories

### Draws Objects and Formats

Functions for creating and converting between five supported formats:
- `draws_array`
- `draws_df`
- `draws_list`
- `draws_matrix`
- `draws_rvars`

### Working with Draws Objects

Operations include:
- Binding draws
- Extracting variables
- Merging chains
- Subsetting
- Renaming variables
- Resampling
- Weighting
- Other modifications to draws objects

### Summarizing and Diagnosing

Computational functions for summary statistics and convergence diagnostics:
- **Rhat** -- Potential scale reduction statistic
- **ESS variants** -- Effective sample size (bulk, tail, basic, quantile)
- **MCSE** -- Monte Carlo standard error (mean, median, quantile, sd)
- **Pareto smoothing diagnostics**

### Rvar-Specific Functionality

The `rvar` (random variable) datatype has dedicated methods:
- Matrix operations
- Slicing
- Density/CDF/quantile functions
- Summaries both over and within draws

## Scale

The package includes approximately 100+ functions organized by use case, including utilities for:
- Extracting variables
- Computing quantiles
- Calculating entropy and dissention measures
- Performing Pareto diagnostics

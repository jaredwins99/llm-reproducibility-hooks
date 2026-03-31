# The Posterior R Package: Tools for Working with Posterior Distributions

Source: https://mc-stan.org/posterior/

posterior package (version 1.6.0). Designed for users and developers working with Bayesian models. Authors: Paul-Christian Burkner, Jonah Gabry, Matthew Kay, Aki Vehtari.

Code licensed under BSD 3-clause; documentation under CC-BY 4.0.

## Primary Goals

- Convert efficiently between different posterior/prior distribution draw formats
- Offer consistent methods for common draw operations (subsetting, binding, mutating)
- Generate convenient draw summaries
- Implement lightweight state-of-the-art posterior inference diagnostics

## Supported Draw Formats

1. **draws_array**: Iterations x chains x variables array structure
2. **draws_matrix**: Draws (iterations x chains) x variables array
3. **draws_df**: Data frame format with `.chain`, `.iteration`, `.draw` metadata columns
4. **draws_list**: List containing one sublist per chain with named variable vectors
5. **draws_rvars**: List of random variable objects, one per variable

Each format includes conversion methods (`as_draws_<format>`) enabling seamless transitions between formats.

## Key Operations

### Subsetting

`subset_draws()` allows extraction based on iterations, chains, or variables. Standard R subsetting syntax also works, with the notable behavior that dimensions with single levels are never dropped.

### Mutating Variables

`mutate_variables()` enables transformations of existing variables. Since draws represent the joint posterior distribution, any function of original variables produces valid draws from that transformed variable's distribution.

### Renaming

`rename_variables()` modifies variable names, supporting both scalar and vector parameter renaming, including individual indexed elements.

### Binding

`bind_draws()` combines multiple draw objects along specified dimensions (draw, iteration, chain, or variable).

## Summaries and Diagnostics

### Basic Usage

`summarise_draws()` generates comprehensive statistics including:
- Mean, median, standard deviation, median absolute deviation
- Quantiles
- Convergence diagnostics: Rhat, ess_bulk, ess_tail

### Customization Options

- Specify particular summary statistics as function names or definitions
- Rename output columns via name-value pairs
- Apply custom functions accepting numeric vectors/matrices returning single values
- Use lambda-like formula syntax following rlang conventions

### Additional Diagnostics

Beyond default diagnostics, posterior provides:
- Effective sample size variants
- Monte Carlo standard errors for quantiles and standard deviations
- Experimental diagnostics like R*

## Additional Methods

- `order_draws()`: Organize by iteration/chain
- `repair_draws()`: Ensure consistent numbering
- `resample_draws()`: Reweight according to specifications
- `thin_draws()`: Reduce size and autocorrelation
- `weight_draws()`: Add per-draw weights
- `extract_variable()`: Obtain single variable vector
- `extract_variable_matrix()`: Get iterations x chains matrix
- `merge_chains()` / `split_chains()`: Manipulate chain structure

## Format Compatibility

Converts from base R objects (matrices, arrays) and objects from **coda** and **rjags** packages.

## Installation

```r
# Stable
install.packages("posterior")

# Development
remotes::install_github("stan-dev/posterior")
```

## Example Dataset

Documentation uses the eight schools hierarchical meta-analysis model (Gelman et al., 2013), containing per-school estimates (theta[1]-theta[8]), overall mean (mu), and standard deviation (tau).

## References

- Gelman et al. (2013). Bayesian Data Analysis, Third Edition
- Vehtari et al. (2020). "Rank-normalization, folding, and localization: An improved Rhat for assessing convergence of MCMC"

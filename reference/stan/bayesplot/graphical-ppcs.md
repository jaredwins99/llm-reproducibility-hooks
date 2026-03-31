# Graphical Posterior Predictive Checks Using Bayesplot

Source: https://mc-stan.org/bayesplot/articles/graphical-ppcs.html

bayesplot package (version 1.15.0). Provides tools for creating graphical displays that compare observed data to simulated data from the posterior predictive distribution.

## Core Concept

"If a model is a good fit then we should be able to use it to generate data that looks a lot like the data we observed." Posterior predictive checking validates models by simulating from the posterior predictive distribution and visually comparing those simulations to actual observations.

## Mathematical Framework

The posterior predictive distribution:

```
p(y_tilde | y) = integral p(y_tilde | theta) p(theta | y) d_theta
```

For each of S parameter draws from the posterior, researchers generate N simulated outcomes, creating an S x N matrix of replications (yrep).

## Main PPC Functions

### Histogram and Density Functions

- **`ppc_dens_overlay`**: Overlays observed data distribution with multiple replicated datasets
- **`ppc_hist`**: Separate histograms comparing observed and simulated data

### Test Statistic Functions

- **`ppc_stat`**: Compares test statistics computed across replicated datasets
- **`ppc_stat_grouped`**: Applies statistics within grouping variable levels

## Practical Example

Demonstrates using roach count data to compare Poisson and Negative Binomial regression models:

- The **Poisson** model underestimated zeros
- The **Negative Binomial** better captured zero-inflation but sometimes predicted unrealistically large values

## Integration Approach

Other Bayesian packages can implement `pp_check` methods for their model objects, enabling seamless access to bayesplot visualizations. Both **rstanarm** and **brms** packages currently use this approach.

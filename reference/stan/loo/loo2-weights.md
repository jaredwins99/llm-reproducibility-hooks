# Bayesian Stacking and Pseudo-BMA Weights Using the loo Package

Source: https://mc-stan.org/loo/articles/loo2-weights.html

Authored by Aki Vehtari and Jonah Gabry. Demonstrates functionality in loo v2.0.0 for computing Bayesian stacking and Pseudo-BMA weighting methods.

## Background

References the foundational paper by Yao, Vehtari, Simpson, and Gelman (2018), which addresses limitations of traditional Bayesian model averaging in the M-open setting -- situations where the true data-generating process is not among the candidate models being evaluated.

Stacking of predictive distributions is preferred to alternatives including stacking of means, traditional BMA, and Pseudo-BMA, with bootstrapped-Pseudo-BMA offered as a computationally efficient approximation.

## Core Methods Compared

Four weighting approaches are demonstrated:

1. **WAIC weights** -- Classical Akaike-style weighting
2. **Pseudo-BMA weights** -- Without Bayesian bootstrap
3. **Pseudo-BMA+ weights** -- With Bayesian bootstrap
4. **Bayesian stacking weights** -- Optimal linear combination

## Practical Examples

### Example 1: Primate Milk

Four models predict milk kilocalories using neocortex percentage and/or log body mass. While all methods favor the model incorporating both predictors, stacking weights handle repeated similar models more effectively than WAIC weights.

### Example 2: Oceanic Tool Complexity

Three Poisson regression models predict tool kit complexity using population size and contact rates. Stacking assigns zero weight to the full interaction model, since its predictions closely resemble a simpler alternative.

## Simplified Implementation

The `loo_model_weights()` wrapper function streamlines computations, accepting either pointwise log-likelihood matrices or pre-computed LOO objects directly.

## References

- McElreath, *Statistical Rethinking* (2016)
- Multiple peer-reviewed papers on Bayesian model evaluation and importance sampling diagnostics

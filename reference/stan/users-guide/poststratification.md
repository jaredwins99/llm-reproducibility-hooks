# Poststratification

## Overview

Poststratification is a statistical technique for adjusting non-representative samples by partitioning populations into subgroups and weighting estimates based on known population sizes. The approach combines survey methodology with Bayesian modeling, particularly through multilevel regression and poststratification (MRP).

## Core Concepts

**Stratification vs. Poststratification**: Stratification divides populations before sampling to reduce variance. Poststratification adjusts samples after model fitting, making it valuable for "convenience samples or other observational data" that lack initial stratification.

## Key Applications

### Earth Science Example
Large-scale soil-carbon models estimate global carbon levels by dividing Earth into grid cells, predicting carbon concentration for each cell's characteristics, then aggregating predictions weighted by cell size.

### Polling Example
A university poll surveyed students across three groups (undergraduate, graduate, continuing education) with different support levels. Population-weighted estimates adjust for the actual student body composition rather than sample composition.

## Mathematical Framework

For a simple binomial model with J groups:
- Data model: a_j ~ binomial(A_j, θ_j) where a_j represents positive responses and A_j represents total respondents
- Population estimate: φ = Σ(θ_j · N_j) / Σ(N_j)

## Bayesian Implementation

Posterior draws from θ|y are combined with known population sizes to generate posterior distributions for population-level quantities. This propagates uncertainty through predictive inference, producing credible intervals and posterior distributions rather than point estimates.

## Regression-Based Poststratification

When demographic features multiply into numerous strata (potentially thousands), direct parameter estimation becomes infeasible due to sparse data per group. Logistic regression reduces parameterization by treating demographic features additively rather than multiplicatively.

## Multilevel Regression and Poststratification (MRP)

Adding hierarchical priors to regression coefficients enables partial pooling, stabilizing estimates when individual cells contain few observations. Hyperpriors on group-level standard deviations allow data to determine appropriate shrinkage levels.

### Handling Non-Identifiability

Multiple intercepts introduce weak non-identifiability. Solutions include:

**Hard constraints**: Sum-to-zero restrictions enforce unique solutions
**Soft constraints**: Secondary priors concentrate coefficient sums near zero without elimination

## Stan Implementation

A complete MRP model includes:
- Individual-level predictors (age, income, state)
- Hierarchical priors on regression coefficients
- Poststratification in generated quantities block
- Population arrays P encoding demographic structure

Key technical choices:
- Non-centered parameterization via `multiplier` transform for sampling efficiency
- Binomial coding for grouped data reduces computation
- Binary features coded as epsilon/-epsilon pairs enforcing sum-to-zero constraints
- Group-level predictors added to both model and poststratification formulas

## Efficiency Considerations

Working with expectations rather than sampling uncertainty during poststratification improves computational efficiency. The Rao-Blackwell theorem supports this approach, particularly for discrete quantities.

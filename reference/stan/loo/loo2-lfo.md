# Approximate Leave-Future-Out Cross-Validation for Bayesian Time Series Models

Source: https://mc-stan.org/loo/articles/loo2-lfo.html

## Overview

Presents PSIS-LFO-CV, an algorithm for assessing predictive performance in time series models without requiring expensive full model refits.

## Key Concepts

### M-Step-Ahead Prediction (M-SAP)

The process of using observed time series data to generate forecasts for M future observations. As the authors note, "the best we can do is to use methods for approximating the expected predictive performance of our models using only the observations of the time series we already have."

### Why LFO Instead of LOO

Standard leave-one-out cross-validation is inappropriate for time series because it violates temporal ordering by allowing future data to influence past predictions. Leave-future-out methods respect causality.

## Algorithm Components

The PSIS-LFO-CV approach involves:

1. **Initial Fit**: Fit the model using the first L observations (minimum required for reliable predictions)

2. **Iterative Approximation**: For subsequent observations, compute importance-weighted predictions using:
   - Raw importance ratios derived from likelihood ratios
   - PSIS stabilization to prevent extreme weights

3. **Adaptive Refitting**: Monitor the Pareto k shape parameter; when it exceeds threshold tau (typically 0.7), refit the model at that point and restart the process

## Case Study Results

Using Lake Huron water level data (98 annual observations, 1875-1972):

**1-Step-Ahead Predictions:**
- Exact ELPD: -92.31
- Approximate ELPD: -92.44
- Required only 2 model refits
- Maximum difference: 0.08

**4-Step-Ahead Predictions:**
- Exact ELPD: -405.52
- Approximate ELPD: -409.08
- Larger M increases variation in approximations

## Advantages

The algorithm "typically only requires refitting the time-series model a small number times and will make LFO-CV tractable for many more realistic applications than previously possible," dramatically reducing computational burden compared to exact cross-validation.

## References

Primary paper: Burkner, Gabry, & Vehtari (2020) in *Journal of Statistical Computation and Simulation*

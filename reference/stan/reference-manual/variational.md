# Variational Inference

## Overview

Stan implements Automatic Differentiation Variational Inference (ADVI), as described by Kucukelbir et al. (2017). The algorithm optimizes the Evidence Lower Bound (ELBO) using stochastic gradient ascent in real-coordinate space.

## Stochastic Gradient Ascent

The core algorithm uses noisy yet unbiased gradient estimates obtained through automatic differentiation and Monte Carlo integration. It ascends these gradients with an adaptive stepsize sequence while evaluating the ELBO through Monte Carlo integration. Convergence assessment mirrors Stan's optimization relative tolerance approach.

### Monte Carlo Approximation of the ELBO

ADVI approximates "the variational objective function, the ELBO" using Monte Carlo integration. The parameter `elbo_samples` controls the number of draws; the recommended default is 100. The ELBO evaluation occurs every `eval_elbo` iterations, which also defaults to 100.

### Monte Carlo Approximation of the Gradients

Gradient approximation uses `grad_samples` draws, with a recommended default of 1. Though this produces noisy estimates, stochastic gradient ascent effectively follows such gradients despite the noise.

### Adaptive Stepsize Sequence

The algorithm employs a finite-memory version of AdaGrad (Duchi, Hazan, and Singer 2011). A single exposed parameter, `eta`, undergoes warmup adaptation. The procedure performs heuristic searching across eta values spanning five orders of magnitude.

### Assessing Convergence

ADVI monitors ELBO progression and "heuristically determines a rolling window over which it computes the average and the median change of the ELBO." When either metric falls below the threshold `tol_rel_obj`, convergence is declared. The ELBO change calculation matches Stan's optimization module methodology.

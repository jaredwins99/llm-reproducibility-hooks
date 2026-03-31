# Laplace Approximation in Stan

## Overview

Stan implements a Laplace approximation algorithm for obtaining draws from an approximated posterior distribution. The method operates in unconstrained parameter space, then transforms results back to the constrained space.

## Algorithm Description

### Mode Estimation and Hessian Computation

The algorithm begins with an estimate of the mode theta-hat. The Hessian H(theta-hat) is calculated using central finite differences of the model functor.

### Cholesky Factorization

The algorithm computes the Cholesky factor of the negative inverse Hessian:

R^{-1} = chol(-H(theta-hat)) \ I

### Draw Generation

Each draw is generated on the unconstrained scale by:

1. Sampling theta^std(m) ~ normal(0, I)
2. Computing draw m as: theta^(m) = theta-hat + R^{-1} * theta^std(m)
3. Transforming theta^(m) back to the constrained scale

## Computational Complexity

The algorithm has significant computational costs:

- **One-time overhead**: O(N^3) for Cholesky factorization in N dimensions
- **Gradient calculations**: 2N gradient evaluations required, scaling as O(N^2) at best
- **Per-draw cost**: O(N^2) operations (matrix multiplication with Cholesky factor)
- **Total cost for M draws**: O(N^3 + M * N^2)

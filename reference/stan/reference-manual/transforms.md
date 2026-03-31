# Stan Reference Manual: Constraint Transforms

## Overview

Stan automatically transforms constrained parameters to unconstrained variables during Hamiltonian dynamics simulation. This chapter documents the mathematical basis for these transformations.

## Key Principle

"Stan converts models to C++ classes which define probability functions with support on all of R^K, where K is the number of unconstrained parameters needed to define the constrained parameters defined in the program."

## Major Transform Categories

### Scalar Bounds

**Lower Bounded**: Variables with lower bound *a* use logarithmic transform: Y = log(X - a), with inverse X = exp(Y) + a and Jacobian exp(y).

**Upper Bounded**: Variables with upper bound *b* use: Y = log(b - X), with inverse X = b - exp(Y) and Jacobian exp(y).

**Both Bounds**: For interval (a,b), Stan uses scaled logit transform:
- Transform: Y = logit((X-a)/(b-a))
- Inverse: X = a + (b-a) * logit^-1(Y)
- Jacobian: (b-a) * logit^-1(y) * (1-logit^-1(y))

### Vector Constraints

**Ordered Vector**: Maps increasing sequences using first element directly, then logarithmic differences: y_k = log(x_k - x_{k-1}) for k > 1.

**Unit Simplex**: Recent versions use softmax of sum-to-zero vector rather than stick-breaking. The Jacobian determinant equals the product of all simplex components.

**Sum-to-Zero Vector**: Uses orthogonal Helmert basis ensuring equal marginal variances across constrained values.

### Matrix Constraints

**Correlation Matrices**: Implements Lewandowski-Kurowicka-Joe (LKJ) transform via hyperbolic tangent and Cholesky factors.

**Covariance Matrices**: Cholesky decomposition combined with log-transform of diagonal elements. Full Jacobian: 2^K * prod(z_{k,k}^{K-k+2})

**Unit Vector**: Normalizes unconstrained vector by its Euclidean norm. Undefined at zero but measure-zero event during sampling.

## Important Implementation Note

"Stan's arithmetic is implemented using double-precision floating-point numbers, which may cause computation to behave differently than mathematics." Boundary values may be rounded, and CmdStan outputs with 8-digit precision by default.

## References

Key citations include Lewandowski et al. (2009) on correlation matrices, Muller (1959) on uniform sphere generation, and Lancaster (1965) on Helmert matrices.

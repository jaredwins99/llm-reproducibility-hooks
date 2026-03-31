# Correlation Matrix Distributions

## Overview

This documentation covers distributions with support on correlation matrices and their Cholesky factors. When modeling correlation matrices, it is computationally preferable to work with Cholesky factors rather than the matrices themselves.

To recover posterior correlations, use the generated quantities block:

```stan
generated quantities {
  corr_matrix[K] Sigma;
  Sigma = multiply_lower_tri_self_transpose(L);
}
```

## LKJ Correlation Distribution

### Probability Density Function

For eta > 0, if Sigma is a positive-definite symmetric matrix with unit diagonal (correlation matrix):

The density is proportional to det(Sigma)^(eta-1).

The expectation is the identity matrix for any positive eta value, with behavior dependent on the shape parameter:

- **eta = 1**: uniform density over correlation matrices
- **eta > 1**: identity matrix is modal; density peaks sharply at identity for larger eta values
- **0 < eta < 1**: density has a trough at the identity matrix
- **For unknown eta**: Jeffreys prior involves the trigamma function psi_1()

Reference: Lewandowski, Kurowicka, and Joe (2009) on generating random correlation matrices using vines and extended onion methods.

### Distribution Statement

```stan
y ~ lkj_corr(eta)
```

Available since version 2.3.

### Stan Functions

**`real lkj_corr_lpdf(matrix y | real eta)`**
Computes log LKJ density for correlation matrix y. Note: `lkj_corr_cholesky_lpdf` is faster, more numerically stable, uses less memory, and is preferred.
Available since 2.12.

**`real lkj_corr_lupdf(matrix y | real eta)`**
Computes log LKJ density for correlation matrix y, dropping constant terms. `lkj_corr_cholesky_lupdf` is preferred.
Available since 2.25.

**`matrix lkj_corr_rng(int K, real eta)`**
Generates random LKJ correlation matrix of order K. May only be used in transformed data and generated quantities blocks.
Available since 2.0.

## Cholesky LKJ Correlation Distribution

Stan provides an implicit parameterization via Cholesky factors, which should be used instead of explicit parameterization. Example:

```stan
L ~ lkj_corr_cholesky(2.0); # implies L * L' ~ lkj_corr(2.0);
```

Parameters should be declared as:

```stan
parameters {
  cholesky_factor_corr[K] L;
}
```

Rather than using `corr_matrix[K] Sigma`.

### Probability Density Function

For eta > 0, if L is a K x K lower-triangular Cholesky factor of a symmetric positive-definite matrix with unit diagonal:

The density is proportional to |J| det(LL^T)^(eta-1), which equals prod_{k=2}^K L_{kk}^(K-k+2*eta-2).

A valid Cholesky factor L requires:
- L_{k,k} > 0 for k in 1:K
- Each row L_k has unit Euclidean length

Even when eta=1, the density is non-constant for L, though it is constant for LL^T.

### Distribution Statement

```stan
L ~ lkj_corr_cholesky(eta)
```

Available since 2.4.

### Stan Functions

**`real lkj_corr_cholesky_lpdf(matrix L | real eta)`**
Computes log LKJ density for lower-triangular Cholesky factor L of a correlation matrix.
Available since 2.12.

**`real lkj_corr_cholesky_lupdf(matrix L | real eta)`**
Computes log LKJ density for lower-triangular Cholesky factor L, dropping constant terms.
Available since 2.25.

**`matrix lkj_corr_cholesky_rng(int K, real eta)`**
Generates random Cholesky factor of correlation matrix distributed LKJ with shape eta. May only be used in transformed data and generated quantities blocks.
Available since 2.4.

# Covariance Matrix Distributions

## Overview

This reference documents probability distributions for symmetric, positive-definite KxK matrices and their Cholesky factors (square, lower triangular matrices with positive diagonal elements).

## Wishart Distribution

### Probability Density Function

For K in N, nu in (K-1,inf), and symmetric positive-definite S in R^(KxK), the Wishart density is:

Wishart(W | nu,S) = 1/(2^(nu*K/2)) * 1/Gamma_K(nu/2) * |S|^(-nu/2) * |W|^((nu-K-1)/2) * exp(-(1/2)*tr(S^{-1}*W))

Where tr() is the matrix trace and Gamma_K() is the multivariate Gamma function.

### Distribution Statement

`W ~ wishart(nu, Sigma)`

### Stan Functions

- `wishart_lpdf(matrix W | real nu, matrix Sigma)` - Returns log probability density (Available since 2.12)
- `wishart_lupdf(matrix W | real nu, matrix Sigma)` - Returns log density dropping constant terms (Available since 2.25)
- `wishart_rng(real nu, matrix Sigma)` - Generates Wishart variate; transforms data/generated quantities blocks only (Available since 2.0)

## Wishart Distribution, Cholesky Parameterization

Uses Cholesky factors for both variate and parameter. If S and W are positive definite with Cholesky factors L_S and L_W (S = L_S L_S^T, W = L_W L_W^T):

L_W ~ WishartCholesky(nu, L_S) if and only if W ~ Wishart(nu, S)

### Probability Density Function

WishartCholesky(L_W | nu,L_S) = Wishart(L_W L_W^T | nu,L_S L_S^T) * |J_{f^{-1}}|

Log absolute determinant: log|J_{f^{-1}}| = K*log(2) + sum (K-k+1)*log((L_W)_{k,k})

Errors raised if nu <= K-1 or if matrices aren't proper Cholesky factors.

### Stan Functions

- `wishart_cholesky_lpdf(matrix L_W | real nu, matrix L_S)` - Log Wishart density for Cholesky factor (Available since 2.30)
- `wishart_cholesky_lupdf(matrix L_W | real nu, matrix L_S)` - Log density dropping constants (Available since 2.30)
- `wishart_cholesky_rng(real nu, matrix L_S)` - Generates Cholesky factor (Available since 2.30)

## Inverse Wishart Distribution

### Probability Density Function

InvWishart(W | nu,S) = 1/(2^(nu*K/2)) * 1/Gamma_K(nu/2) * |S|^(nu/2) * |W|^(-(nu+K+1)/2) * exp(-(1/2)*tr(S*W^{-1}))

### Distribution Statement

`W ~ inv_wishart(nu, Sigma)`

### Stan Functions

- `inv_wishart_lpdf(matrix W | real nu, matrix Sigma)` - Log probability density (Available since 2.12)
- `inv_wishart_lupdf(matrix W | real nu, matrix Sigma)` - Log density dropping constants (Available since 2.25)
- `inv_wishart_rng(real nu, matrix Sigma)` - Generates inverse Wishart variate (Available since 2.0)

## Inverse Wishart Distribution, Cholesky Parameterization

L_W ~ InvWishartCholesky(nu, L_S) if and only if W ~ InvWishart(nu, S)

### Probability Density Function

InvWishartCholesky(L_W | nu,L_S) = InvWishart(L_W L_W^T | nu,L_S L_S^T) * |J_{f^{-1}}|

Log absolute determinant: log|J_{f^{-1}}| = K*log(2) + sum (K-k+1)*log((L_W)_{k,k})

### Stan Functions

- `inv_wishart_cholesky_lpdf(matrix L_W | real nu, matrix L_S)` - Log inverse Wishart density (Available since 2.30)
- `inv_wishart_cholesky_lupdf(matrix L_W | real nu, matrix L_S)` - Log density dropping constants (Available since 2.30)
- `inv_wishart_cholesky_rng(real nu, matrix L_S)` - Generates Cholesky factor (Available since 2.30)

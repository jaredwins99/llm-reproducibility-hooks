# Hidden Markov Models

## Overview

An elementary first-order Hidden Markov model is a probabilistic framework for modeling N observations (y_n) and N hidden states (x_n), fully defined by conditional distributions p(y_n | x_n, phi) and p(x_n | x_{n-1}, phi).

When states take discrete, finite values in {1, 2, ..., K}, Stan enables marginalization of x to compute p(y | phi).

## Key Components

**Conditional Observational Distribution:** A K x N matrix omega where omega_{kn} = p(y_n | x_n = k, phi)

**Transition Matrix:** A K x K matrix Gamma where Gamma_{ij} = p(x_n = j | x_{n-1} = i, phi). Each row forms a probability distribution (simplex). Stan supports stationary transitions using a single matrix for all transitions.

**Initial State Vector:** A K-vector rho where rho_k = p(x_0 = k | phi)

## Stan Functions

### hmm_marginal
```
real hmm_marginal(matrix log_omega, matrix Gamma, vector rho)
```
Returns the log probability density of y with x_n integrated out at each iteration.

**Parameters:**
- `log_omega`: log density of each output
- `Gamma`: transition matrix
- `rho`: initial state probability

*Available since 2.24*

### hmm_latent_rng
```
array[] int hmm_latent_rng(matrix log_omega, matrix Gamma, vector rho)
```
Returns a length N array of integers over {1, ..., K}, sampled from the joint posterior distribution p(x | phi, y). Restricted to transformed data and generated quantities blocks.

*Available since 2.24*

### hmm_hidden_state_prob
```
matrix hmm_hidden_state_prob(matrix log_omega, matrix Gamma, vector rho)
```
Returns a K x N matrix of marginal posterior probabilities for each hidden state value. The nth column is a simplex; A_{ij} = p(x_j = i | phi, y). Restricted to transformed data and generated quantities blocks.

*Available since 2.24*

# Simplex Distributions

## Overview

The simplex probabilities have support on the unit K-simplex for a specified K. A K-dimensional vector theta is a unit K-simplex if theta_k >= 0 for k in {1,...,K} and sum_{k=1}^K theta_k = 1.

## Dirichlet Distribution

### Probability Density Function

If K in N and alpha in (R+)^K, then for theta in K-simplex:

Dirichlet(theta|alpha) = Gamma(sum_{k=1}^K alpha_k) / prod_{k=1}^K Gamma(alpha_k) * prod_{k=1}^K theta_k^(alpha_k-1)

**Warning:** If any component of theta satisfies theta_i = 0 or theta_i = 1, the probability is 0 and the log probability is -inf. The distribution requires strictly positive parameters with alpha_i > 0 for each i.

### Meaning of Dirichlet Parameters

A symmetric Dirichlet prior uses the form [alpha, ..., alpha]^T. Example Stan code:

```stan
data {
  int<lower=1> K;
  real<lower=0> alpha;
}
generated quantities {
  vector[K] theta = dirichlet_rng(rep_vector(alpha, K));
}
```

For K = 10 with alpha = 1 (uniform distribution), sample draws are:
- 0.17 0.05 0.07 0.17 0.03 0.13 0.03 0.03 0.27 0.05
- 0.08 0.02 0.12 0.07 0.52 0.01 0.07 0.04 0.01 0.06

The distribution is not uniform over marginal probabilities. "As the size of the simplex grows, the marginal draws become more and more concentrated below (not around) 1/K."

With small alpha values (e.g., alpha = 0.001), draws concentrate at simplex corners with one value near 1 and others near 0.

With large alpha values (e.g., alpha = 1000), draws become increasingly uniform, with all components approximately 0.10.

### Distribution Statement

```
theta ~ dirichlet(alpha)
```

Increments target log probability density with `dirichlet_lupdf(theta | alpha)`.

Available since 2.0

### Stan Functions

The Dirichlet probability functions are overloaded to allow simplex theta and prior counts alpha to be vectors or row vectors. Density functions are vectorized.

#### `dirichlet_lpdf`

```
real dirichlet_lpdf(vectors theta | vectors alpha)
```

The log of the Dirichlet density for simplex(es) theta given prior counts (plus one) alpha.

Available since 2.12, vectorized in 2.21

#### `dirichlet_lupdf`

```
real dirichlet_lupdf(vectors theta | vectors alpha)
```

The log of the Dirichlet density for simplex(es) theta given prior counts (plus one) alpha, dropping constant additive terms.

Available since 2.25

#### `dirichlet_rng`

```
vector dirichlet_rng(vector alpha)
```

Generates a Dirichlet variate with prior counts (plus one) alpha; usable only in transformed data and generated quantities blocks.

Available since 2.0

# Efficiency Tuning - Complete Content

## Overview

This chapter from the Stan User's Guide provides comprehensive techniques for optimizing Stan code. The document emphasizes that "efficiency involves both the amount of time required for a computation and the amount of memory required."

## Key Sections

### What is Efficiency?

The guide distinguishes between asymptotic efficiency and constant factors. While computer science typically focuses on algorithmic complexity, practical optimization often involves "cutting runtime in half or more."

### Statistical vs. Computational Efficiency

Two distinct concepts emerge:
- **Computational efficiency**: Time/memory for specific calculations
- **Statistical efficiency**: Requiring fewer algorithm steps through improved model formulation

### Model Conditioning and Curvature

The Hessian matrix measures posterior curvature via second derivatives. The **condition number** (ratio of largest to smallest eigenvalues) gauges problem difficulty. Better conditioning means:
- Easier adaptation for gradient-based algorithms
- Parameters with unit scale and reduced correlation
- Consistent curvature across parameter space

### Well-Specified Models

Model misspecification causes performance degradation. Counter-intuitively, more complex hierarchical models often run faster than simpler ones with mismatched priors.

## Reparameterization Techniques

### Neal's Funnel Example

The classic example demonstrates how changing from centered to non-centered parameterization dramatically improves sampling. Original form:
```stan
parameters {
  real y;
  vector[9] x;
}
model {
  y ~ normal(0, 3);
  x ~ normal(0, exp(y/2));
}
```

Reparameterized version separates hierarchical levels, making sampling easier through independent standard normals.

### Cauchy Distribution

Heavy-tailed distributions challenge Hamiltonian Monte Carlo. Solution: transform via inverse CDF using uniform distribution, replacing direct Cauchy sampling with:
```stan
parameters {
  real<lower=-pi() / 2, upper=pi() / 2> beta_unif;
}
transformed parameters {
  real beta;
  beta = mu + tau * tan(beta_unif);
}
```

### Student-t Distribution

Use gamma-mixture representation: generate precision τ from Gamma(ν/2, ν/2), then β from normal with scale τ^(-0.5).

### Hierarchical Models

**Centered parameterization** exhibits inefficiency when data is limited:
```stan
parameters {
  real mu_beta;
  real<lower=0> sigma_beta;
  vector[K] beta;
}
model {
  beta ~ normal(mu_beta, sigma_beta);
}
```

**Non-centered parameterization** decouples parameters:
```stan
parameters {
  real mu_beta;
  real<lower=0> sigma_beta;
  vector[K] beta_raw;
}
transformed parameters {
  vector[K] beta;
  beta = mu_beta + sigma_beta * beta_raw;
}
model {
  beta_raw ~ std_normal();
}
```

### Multivariate Reparameterizations

For multivariate normal priors with covariance Σ:
```stan
transformed data {
  matrix[K, K] L;
  L = cholesky_decompose(Sigma);
}
parameters {
  vector[K] alpha;
}
transformed parameters {
  vector[K] beta;
  beta = mu + L * alpha;
}
model {
  alpha ~ std_normal();
}
```

Benefits include reduced element dependence and avoiding matrix inversion.

## Vectorization

### Gradient Bottleneck

Stan spends most computation on gradient calculations. Vectorization reduces intermediate allocations during automatic differentiation.

### Vectorizing Summations

Instead of:
```stan
for (n in 1:N) {
  total += foo(n,...);
}
```

Use:
```stan
{
  vector[N] summands;
  for (n in 1:N) {
    summands[n] = foo(n,...);
  }
  total = sum(summands);
}
```

Despite extra allocation, the differentiation savings dominate.

### Matrix Operations

Most efficient linear regression form:
```stan
data {
  matrix[N, K] x;
  vector[N] y;
}
parameters {
  vector[K] beta;
}
model {
  y ~ normal(x * beta, 1);
}
```

Encapsulated operations outperform sequential operations.

### Vectorized Probability Functions

Many distributions support vectorized arguments. When all arguments match dimensions, single function call replaces loops.

### Reshaping Data

Sometimes reorganizing data by group enables better vectorization than universal vectorization approaches.

## Sufficient Statistics

### Bernoulli

Replace individual observations with binomial sufficient statistic:
```stan
sum(y) ~ binomial(N, theta);
```

### Normal

Express likelihood using mean and variance:
```stan
transformed data {
  real mean_y = mean(y);
  real<lower=0> var_y = variance(y);
}
model {
  mean_y ~ normal(mu, sigma / sqrt(N));
  var_y ~ gamma(nm1_over2, nm1_over2 / sigma^2);
}
```

### Poisson

Sum observations and scale parameter: `sum(y) ~ poisson(size(y) * lambda);`

## Additional Optimization Strategies

### Avoiding Validation

Prevent duplicate validation of covariance matrices by declaring unconstrained intermediate forms when validation happens elsewhere.

### Common Subexpressions

Cache repeated calculations:
```stan
vector[N] exp_theta = exp(theta);
// Use exp_theta multiple times
```

### Exploiting Conjugacy

When prior and likelihood conjugate, use updated hyperparameters directly.

### Standardizing Predictors

Scale predictors to zero mean, unit variance for:
- Faster MCMC convergence
- Reduced parameterization sensitivity
- Improved coefficient interpretation

Formulas for recovery:
- β = β'/sd_x
- α = α' - β'(mean_x/sd_x)

### Standard Normal Shortcut

Use `y ~ std_normal();` instead of `y ~ normal(0, 1);` for efficiency.

## Map-Reduce

Map-reduce improves scalability by storing only mapped function Jacobians, improving memory locality and execution speed through reduced overhead.

---

**References cited**: Betancourt & Girolami (2013), Neal (2003), Papaspiliopoulos et al. (2007), Zyczkowski & Sommers (2001)

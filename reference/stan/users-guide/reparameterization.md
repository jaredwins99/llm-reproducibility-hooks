# Reparameterization and Change of Variables

## Overview

Stan supports two related but distinct techniques for handling parameter transformations: reparameterization and changes of variables. These approaches allow flexible model specification with different computational characteristics.

## Theoretical Foundation

A Bayesian posterior represents a "probability measure" that remains invariant across parameterizations. However, Stan implements probability densities, which are parameterization-dependent. This means the same model can be expressed multiple ways with different computational performance.

As Gelman (2004) notes, "a change of parameterization often carries suggestions of how the model might change" because practitioners naturally select certain prior classes with particular parameterizations.

## Reparameterizations

Reparameterizations transform parameters without adjusting the probability density. They can be implemented in the `transformed parameters` block or within the `model` block.

### Beta and Dirichlet Priors

**Beta Distribution Example:**

Rather than directly specifying hyperpriors on beta parameters α and β, it's often more natural to work with:
- Mean: φ = α / (α + β)
- Total count: λ = α + β

```stan
parameters {
  real<lower=0, upper=1> phi;
  real<lower=0.1> lambda;
}
transformed parameters {
  real<lower=0> alpha = lambda * phi;
  real<lower=0> beta = lambda * (1 - phi);
}
model {
  phi ~ beta(1, 1);
  lambda ~ pareto(0.1, 1.5);
  for (n in 1:N) {
    theta[n] ~ beta(alpha, beta);
  }
}
```

**Key point:** No Jacobian adjustment is required because the transformed parameters receive probability distributions, not the original parameters.

**Dirichlet Distribution Example:**

For simplices with K > 1 dimensions, replace scalar means with a simplex parameter:

```stan
parameters {
  simplex[K] phi;
  real<lower=0> kappa;
  array[N] simplex[K] theta;
}
transformed parameters {
  vector[K] alpha = kappa * phi;
}
model {
  phi ~ // ...
  kappa ~ // ...
  for (n in 1:N) {
    theta[n] ~ dirichlet(alpha);
  }
}
```

Here φ represents the expected value of θ, while κ minus K represents the strength of the prior in prior observations.

### Transforming Unconstrained Priors: Probit and Logit

Inverse transformations of CDFs map uniform random variables to standard distributions:
- If u ~ Uniform(0,1), then logit(u) ~ Logistic(0,1)
- If u ~ Uniform(0,1), then Φ⁻¹(u) ~ Normal(0,1)

**Example with logistic prior:**

```stan
parameters {
  real theta_raw;
}
transformed parameters {
  real<lower=0, upper=1> theta = inv_logit(theta_raw);
}
model {
  theta_raw ~ logistic(mu, sigma);
  y ~ foo(theta);
}
```

The prior mean on θ becomes inv_logit(μ). When σ=1 and μ=0, the prior is flat; larger σ produces U-shaped densities.

**Softmax generalization for simplices:**

```stan
parameters {
  vector[K] theta_raw;
}
transformed parameters {
  simplex[K] theta = softmax(theta_raw);
}
model {
  theta_raw ~ multi_normal_cholesky(mu, L_Sigma);
}
```

Mean is controlled by softmax(μ), with covariance structure through the Cholesky factor.

## Changes of Variables

Changes of variables differ from reparameterizations: the transformation itself receives a probability distribution. This requires a Jacobian adjustment equal to the absolute determinant of the transform's Jacobian matrix.

For univariate transforms, the adjustment equals the absolute derivative. Transforms must be monotonic and differentiable. Multivariate transforms must be injective and map R^N to R^N.

### Lognormal Example

If y > 0 with log(y) ~ Normal(μ, σ), then:

p(y) = normal(log y | μ, σ) |d/dy log y| = normal(log y | μ, σ) · 1/y

In log space:

log p(y) = log normal(log y | μ, σ) - log y

**Stan implementation:**

```stan
parameters {
  real<lower=0> y;
}
model {
  log(y) ~ normal(mu, sigma);
  target += -log(y);
}
```

### Change of Variables vs. Transformations

**Transformation approach** (samples, then transforms):
```stan
parameters {
  real<lower=0> y;
}
transformed parameters {
  real<lower=0> y_inv = 1 / y;
}
model {
  y ~ gamma(2, 4);
}
```

**Change-of-variables approach** (transforms, then samples):
```stan
parameters {
  real<lower=0> y_inv;
}
transformed parameters {
  real<lower=0> y = 1 / y_inv;
  target += -2 * log(y_inv);  // Jacobian
}
model {
  y ~ gamma(2, 4);
}
```

The Jacobian adjustment reflects that d/du(1/u) = -u⁻², so log|-u⁻²| = -2 log(u).

### Multivariate Changes of Variables

For vector transforms from u to v, add the log absolute determinant of the Jacobian matrix:

```stan
parameters {
  vector[K] u;
}
transformed parameters {
  vector[K] v;
  matrix[K, K] J;
  // ... compute v and Jacobian matrix J ...
  target += log(abs(determinant(J)));
}
model {
  v ~ // ...
}
```

**Triangular optimization:** When v[k] depends only on u[1],...,u[k], the Jacobian is triangular. The determinant becomes the product of diagonal elements:

```stan
transformed parameters {
  vector[K] J_diag;
  // ... compute diagonal Jacobian entries ...
  target += sum(log(J_diag));
}
```

## Vectors with Varying Bounds

### Varying Lower Bounds

Adding a constant lower bound requires no Jacobian adjustment:

```stan
data {
  int N;
  vector[N] L;
}
parameters {
  vector<lower=L>[N] alpha;
}
```

Equivalent manual approach:

```stan
parameters {
  vector<lower=0>[N] alpha_raw;
}
transformed parameters {
  vector[N] alpha = L + alpha_raw;
}
```

The Jacobian of adding a constant has determinant 1.

### Varying Upper and Lower Bounds

Rescale a (0,1)-constrained variable:

```stan
data {
  int N;
  vector[N] L;
  vector[N] U;
}
parameters {
  vector<lower=L, upper=U>[N] alpha;
}
```

Manual implementation:

```stan
parameters {
  vector<lower=0, upper=1>[N] alpha_raw;
}
transformed parameters {
  vector[N] alpha = L + (U - L) .* alpha_raw;
}
```

When L and U are constants, no Jacobian adjustment is needed.

## Key Takeaways

- **Reparameterization:** Transform parameters for computational convenience; no Jacobian needed
- **Change of variables:** Apply distributions to transformed variables; Jacobian adjustment required
- **Bounds:** Stan handles constraint transforms automatically; manual implementation requires careful Jacobian accounting

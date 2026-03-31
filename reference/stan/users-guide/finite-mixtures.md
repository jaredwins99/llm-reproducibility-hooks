# Finite Mixtures - Complete Content

## Overview

Finite mixture models assume outcomes are drawn from one of several distributions, controlled by a categorical mixing distribution. These models typically have multimodal densities and can be parameterized multiple ways.

## Relation to Clustering

Clustering models represent a particular class of mixture models widely applied in engineering and machine learning. The K-means algorithm is based on normal mixture models, and latent Dirichlet allocation can be viewed as a mixed-membership multinomial mixture model.

## Latent Discrete Parameterization

Consider K normal distributions with locations μₖ ∈ ℝ and scales σₖ ∈ (0,∞), mixed in proportion λ where λₖ ≥ 0 and Σₖ₌₁ᴷ λₖ = 1.

For each outcome yₙ, there is a latent variable zₙ ∈ {1,...,K}:

```
zₙ ~ categorical(λ)
yₙ ~ normal(μ_z[n], σ_z[n])
```

Stan cannot directly sample discrete parameters zₙ, but can marginalize them out.

## Summing Out the Responsibility Parameter

When marginalizing discrete parameters, the mixture density becomes:

```
p_Y(y | λ, μ, σ) = Σₖ₌₁ᴷ λₖ · normal(y | μₖ, σₖ)
```

### Log Sum of Exponentials

The `log_sum_exp` function enables numerically stable computation on the log scale:

```
log_sum_exp(a, b) = log(exp(a) + exp(b))
```

It prevents overflow/underflow by computing:

```
log(exp(a) + exp(b)) = c + log(exp(a-c) + exp(b-c))
```

where c = max(a, b).

**Example:** A mixture of normal(-1, 2) with normal(3, 1) and mixing proportion λ = [0.3, 0.7]:

```stan
parameters {
  real y;
}
model {
  target += log_sum_exp(log(0.3) + normal_lpdf(y | -1, 2),
                        log(0.7) + normal_lpdf(y | 3, 1));
}
```

### Dropping Uniform Mixture Ratios

When mixture proportions are uniform (0.5 for two components or 1/K for K components), the mixing constants can be omitted since they don't affect the proportional density:

```stan
for (n in 1:N) {
  target += log_sum_exp(normal_lpdf(y[n] | mu[1], sigma[1]),
                        normal_lpdf(y[n] | mu[2], sigma[2]));
}
```

This follows from the identity:
```
log_sum_exp(c + a, c + b) = c + log_sum_exp(a, b)
```

### Recovering Posterior Mixture Proportions

The posterior probability that observation yₙ arose from component k is:

```
Pr[zₙ = k | yₙ, μ, σ, λ] =
  (normal(yₙ | μₖ, σₖ) · λₖ) /
  Σₖ'(normal(yₙ | μₖ', σₖ') · λₖ')
```

On the log scale:

```
log Pr[zₙ = k | yₙ, μ, σ, λ] =
  log p(yₙ | zₙ=k, μ, σ) + log Pr[zₙ=k | λ] -
  log_sum_exp_k'(log p(yₙ | zₙ=k', μ, σ) + log p(zₙ=k' | λ))
```

### Estimating Parameters of a Mixture

A complete mixture model with unknown parameters:

```stan
data {
  int<lower=1> K;          // number of mixture components
  int<lower=1> N;          // number of data points
  array[N] real y;         // observations
}
parameters {
  simplex[K] theta;          // mixing proportions
  ordered[K] mu;             // locations of mixture components
  vector<lower=0>[K] sigma;  // scales of mixture components
}
model {
  vector[K] log_theta = log(theta);  // cache log calculation
  sigma ~ lognormal(0, 2);
  mu ~ normal(0, 10);
  for (n in 1:N) {
    vector[K] lps = log_theta;
    for (k in 1:K) {
      lps[k] += normal_lpdf(y[n] | mu[k], sigma[k]);
    }
    target += log_sum_exp(lps);
  }
}
```

Key features:
- `theta` is a unit K-simplex (mixing proportions)
- `mu` is ordered to identify the model
- `sigma` is constrained non-negative with a weakly informative prior
- Local variable `lps` accumulates log contributions

## Vectorizing Mixtures

**Important:** Naive vectorization produces a different model. Proper observation-level mixture:

```stan
for (n in 1:N) {
  target += log_sum_exp(log(lambda)
                          + normal_lpdf(y[n] | mu[1], sigma[1]),
                        log1m(lambda)
                          + normal_lpdf(y[n] | mu[2], sigma[2]));
}
```

or using `log_mix`:

```stan
for (n in 1:N) {
  target += log_mix(lambda,
                    normal_lpdf(y[n] | mu[1], sigma[1]),
                    normal_lpdf(y[n] | mu[2], sigma[2]));
}
```

This defines density:
```
p(y | λ, μ, σ) = Πₙ(λ·normal(yₙ | μ₁, σ₁) + (1-λ)·normal(yₙ | μ₂, σ₂))
```

**Incorrect vectorization:**

```stan
target += log_sum_exp(log(lambda)
                        + normal_lpdf(y | mu[1], sigma[1]),
                      log1m(lambda)
                        + normal_lpdf(y | mu[2], sigma[2]));
```

This implies the entire sequence comes from one component:
```
p(y | λ, μ, σ) = λ·Πₙnormal(yₙ | μ₁, σ₁) + (1-λ)·Πₙnormal(yₙ | μ₂, σ₂)
```

## Inferences Supported by Mixtures

### Mixtures with Unidentifiable Components

When mixture components have exchangeable priors and uniform mixture ratios, the parameters are unidentifiable. This can be resolved through ordering constraints, which allows identification while preserving symmetric priors.

### Inference Under Label Switching

When components are unidentifiable, MCMC labels may switch across chains. Inferences invariant to label switching are sound.

#### Posterior Predictive Distribution

For new observation ỹ:

```
p(ỹ | y) = ∫ₚ p(ỹ | θ) · p(θ | y) dθ
```

This is invariant under label switching:

```stan
data {
  int<lower=0> N_tilde;
  vector[N_tilde] y_tilde;
}
generated quantities {
  vector[N_tilde] log_p_y_tilde;
  for (n in 1:N_tilde) {
    log_p_y_tilde[n]
      = log_mix(lambda,
                normal_lpdf(y_tilde[n] | mu[1], sigma[1]),
                normal_lpdf(y_tilde[n] | mu[2], sigma[2]));
  }
}
```

Compute average log predictive density using `log_sum_exp` of posterior draws.

#### Clustering and Similarity

Probability that observations yᵢ and yⱼ arose from the same component:

```
Pr[zᵢ = zⱼ | y] = ∫ₚ [Σₖ p(zᵢ=k, zⱼ=k, yᵢ, yⱼ | θ)] /
                      [Σₖ Σₘ p(zᵢ=k, zⱼ=m, yᵢ, yⱼ | θ)] · p(θ | y) dθ
```

Compute in generated quantities either by sampling zᵢ and zⱼ or computing in expectation (more statistically efficient).

## Zero-Inflated and Hurdle Models

Both create mixtures of Poisson and Bernoulli PMFs for flexibility with zero outcomes.

### Zero Inflation

Zero-inflated Poisson with probability θ of zero and 1-θ of Poisson(λ):

Likelihood:
```
p(yₙ | θ, λ) = {
  θ + (1-θ)·Poisson(0 | λ)     if yₙ = 0
  (1-θ)·Poisson(yₙ | λ)        if yₙ > 0
}
```

Stan implementation:

```stan
data {
  int<lower=0> N;
  array[N] int<lower=0> y;
}
parameters {
  real<lower=0, upper=1> theta;
  real<lower=0> lambda;
}
model {
  for (n in 1:N) {
    if (y[n] == 0) {
      target += log_sum_exp(log(theta),
                            log1m(theta)
                              + poisson_lpmf(y[n] | lambda));
    } else {
      target += log1m(theta)
                  + poisson_lpmf(y[n] | lambda);
    }
  }
}
```

`log1m(theta)` computes log(1-θ) with numerical stability.

#### Optimizing Zero-Inflated Poisson

Separate zeros and non-zeros for vectorization:

```stan
functions {
  int num_zeros(array[] int y) {
    int sum = 0;
    for (n in 1:size(y)) {
      sum += (y[n] == 0);
    }
    return sum;
  }
}
transformed data {
  int<lower=0> N_zero = num_zeros(y);
  array[N - N_zero] int<lower=1> y_nonzero;
  int N_nonzero = 0;
  for (n in 1:N) {
    if (y[n] == 0) continue;
    N_nonzero += 1;
    y_nonzero[N_nonzero] = y[n];
  }
}
model {
  target
    += N_zero
         * log_sum_exp(log(theta),
                       log1m(theta)
                         + poisson_lpmf(0 | lambda));
  target += N_nonzero * log1m(theta);
  target += poisson_lpmf(y_nonzero | lambda);
}
```

### Hurdle Models

Hurdle models allow deflation (or inflation) of zeros. With probability θ of zero and 1-θ of truncated Poisson (truncated at 0):

Likelihood:
```
p(y | θ, λ) = {
  θ                                            if y = 0
  (1-θ) · Poisson(y | λ) / (1 - PoissonCDF(0 | λ))   if y > 0
}
```

Implementation:

```stan
if (y[n] == 0) {
  target += log(theta);
} else {
  target += log1m(theta) + poisson_lpmf(y[n] | lambda)
            - poisson_lccdf(0 | lambda));
}
```

Optimization note: Since `log(1 - PoissonCDF(0 | λ)) = log(1 - exp(-λ))`, the CCDF can be replaced:

```stan
target += log1m(theta) + poisson_lpmf(y[n] | lambda)
          - log1m_exp(-lambda));
```

This improves speed by ~15%.

Vectorized hurdle model using sufficient statistics:

```stan
functions {
  int num_zero(array[] int y) {
    int nz = 0;
    for (n in 1:size(y)) {
      if (y[n] == 0) {
        nz += 1;
      }
    }
    return nz;
  }
}
transformed data {
  int<lower=0, upper=N> N0 = num_zero(y);
  int<lower=0, upper=N> Ngt0 = N - N0;
  array[N - num_zero(y)] int<lower=1> y_nz;
  {
    int pos = 1;
    for (n in 1:N) {
      if (y[n] != 0) {
        y_nz[pos] = y[n];
        pos += 1;
      }
    }
  }
}
model {
  N0 ~ binomial(N, theta);
  y_nz ~ poisson(lambda);
  target += -Ngt0 * log1m_exp(-lambda);
}
```

## Priors and Effective Data Size in Mixture Models

In a two-component mixture with mixing rate λ, the effective data sizes for estimating each component are λN and (1-λ)N, determined by posterior responsibility rather than just the mixing rate.

### Comparison to Model Averaging

Mixture models differ from model averaging:
- **Mixtures:** Create mixtures at observation level; each observation may come from different components
- **Model Averaging:** Creates mixtures over posteriors of separately fit models using complete data

For similar models, a single expanded model is recommended over averaging. For substantially different models or computational bottlenecks, model averaging after independent fits may be necessary.

When mixture models are appropriate, they're preferable to averaging because "each observation may have arisen from different components."

---

## References

Gelman, A., Carlin, J. B., Stern, D. B., Dunson, D. B., Vehtari, A., & Rubin, D. B. (2013). *Bayesian Data Analysis* (3rd ed.). Chapman & Hall/CRC Press.

Hoeting, J. A., Madigan, D., Raftery, A. E., & Volinsky, C. T. (1999). Bayesian model averaging: A tutorial. *Statistical Science*, 14(4), 382–417.

Lambert, D. (1992). Zero-inflated Poisson regression, with an application to defects in manufacturing. *Technometrics*, 34(1).

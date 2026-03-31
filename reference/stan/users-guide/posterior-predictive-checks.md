# Posterior and Prior Predictive Checks

## Overview

Posterior predictive checks measure how well a model captures relevant data aspects like means, standard deviations, and quantiles. The process involves simulating new replicated datasets from fitted model parameters and comparing statistics between replicated and original data.

Prior predictive checks evaluate priors by generating data according to prior distributions, assessing whether priors are appropriate without data calibration.

## Simulating from the Posterior Predictive Distribution

The posterior predictive distribution represents new observations given previous observations. For replications y^rep of original data y conditioned on parameters θ:

```
p(y^rep | y) = ∫ p(y^rep | θ) · p(θ | y) dθ
```

### Example: Simple Regression Model

**Stan Model:**
```stan
data {
  int<lower=0> N;
  vector[N] x;
  vector[N] y;
}
parameters {
  real alpha;
  real beta;
  real<lower=0> sigma;
}
model {
  alpha ~ normal(0, 2);
  beta ~ normal(0, 1);
  sigma ~ normal(0, 1);
  y ~ normal(alpha + beta * x, sigma);
}
generated quantities {
  array[N] real y_rep = normal_rng(alpha + beta * x, sigma);
}
```

The generated quantities block creates replicated data using the same predictors and estimated parameters.

## Plotting Multiples

Visual comparison uses small multiples plots with original data and several posterior replications.

### Poisson Example

**Complete Stan Model:**
```stan
data {
  int<lower=0> N;
  array[N] int<lower=0> y;
}
transformed data {
  real<lower=0> mean_y = mean(to_vector(y));
  real<lower=0> sd_y = sd(to_vector(y));
}
parameters {
  real<lower=0> lambda;
}
model {
  y ~ poisson(lambda);
  lambda ~ exponential(0.2);
}
generated quantities {
  array[N] int<lower=0> y_rep = poisson_rng(rep_array(lambda, N));
  real<lower=0> mean_y_rep = mean(to_vector(y_rep));
  real<lower=0> sd_y_rep = sd(to_vector(y_rep));
  int<lower=0, upper=1> mean_gte = (mean_y_rep >= mean_y);
  int<lower=0, upper=1> sd_gte = (sd_y_rep >= sd_y);
}
```

When fitting Poisson data with a Poisson model, replications resemble original data. When fitting negative binomial data with a Poisson model, original data stands out due to higher variance—the model fails to capture dispersion.

## Posterior "p-values"

Posterior p-values test whether summary statistics in replicated datasets match original data statistics:

```
Pr[s(y^rep) ≥ s(y) | y]
```

**Important note:** These are not classically calibrated statistics. Values near zero or one indicate poor model fit, but they don't have uniform distributions even with well-specified models.

### Implementation

Indicator variables in the generated quantities block calculate event probabilities:

```stan
generated quantities {
  int<lower=0, upper=1> mean_gt;
  int<lower=0, upper=1> sd_gt;
  {
    array[N] real y_rep = normal_rng(alpha + beta * x, sigma);
    mean_gt = mean(y_rep) > mean(y);
    sd_gt = sd(y_rep) > sd(y);
  }
}
```

The posterior mean of indicator variables equals event probabilities.

### Which Statistics to Test?

Test statistics should ideally be ancillary—testing aspects beyond parameter fit. For normal models, mean and variance are natural parameters. For Poisson models, a single rate parameter controls both mean and variance, so dispersion deserves testing. Other useful statistics include quantiles, maxima, and minima.

## Prior Predictive Checks

Prior predictive checks evaluate prior appropriateness by generating data from:

```
y^sim ~ p(y)
```

This simulates parameters from the prior, then data from the likelihood:

```
θ^sim ~ p(θ)
y^sim ~ p(y | θ^sim)
```

### Coding Prior Predictive Checks

**Poisson Regression Example:**
```stan
data {
  int<lower=0> N;
  vector[N] x;
}
generated quantities {
  real alpha = normal_rng(0, 1);
  real beta = normal_rng(0, 1);
  array[N] real y_sim = poisson_log_rng(alpha + beta * x);
}
```

Running this with Stan's fixed-parameter sampler yields independent draws from the prior.

## Example: Football League Prior Predictive Check

Consider a model for team scoring rates λ_j where teams score according to Poisson(λ_j). Using a gamma(0.5, 0.00001) reference prior:

```stan
data {
  int<lower=0> J;
  array[2] real<lower=0> epsilon;
}
generated quantities {
  array[J] real<lower=0> lambda;
  array[J, J] int y;
  for (j in 1:J) lambda[j] = gamma_rng(epsilon[1], epsilon[2]);
  for (i in 1:J) {
    for (j in 1:J) {
      y[i, j] = poisson_rng(lambda[i]) - poisson_rng(lambda[j]);
    }
  }
}
```

This prior generates unrealistic score differentials exceeding 100 points, concentrating "95% of prior weight on score differentials above 100." Such extreme values are inconsistent with actual football data, indicating an inappropriate prior.

## Mixed Predictive Replication for Hierarchical Models

For hierarchical models, mixed replication keeps hyperparameters fixed at posterior values while replicating lower-level parameters and data.

### Example: Varying Intercept Logistic Regression

**Model Structure:**
```
μ ~ normal(0, 2)
σ ~ lognormal(0, 1)
α_k ~ normal(μ, σ)
y_n ~ bernoulli(logit^-1(α_{kk[n]}))
```

**Stan Implementation:**
```stan
data {
  int<lower=0> K;
  int<lower=0> N;
  array[N] int<lower=1, upper=K> kk;
  array[N] int<lower=0, upper=1> y;
}
parameters {
  real mu;
  real<lower=0> sigma;
  vector<offset=mu, multiplier=sigma>[K] alpha;
}
model {
  mu ~ normal(0, 2);
  sigma ~ lognormal(0, 1);
  alpha ~ normal(mu, sigma);
  y ~ bernoulli_logit(alpha[kk]);
}
generated quantities {
  array[K] real alpha_rep = normal_rng(rep_vector(mu, K), sigma);
  array[N] int<lower=0, upper=1> y_rep =
    bernoulli_logit_rng(alpha_rep[kk]);
}
```

Hyperparameters μ and σ are drawn from the posterior; replicated intercepts and data use posterior hyperparameter values.

## Joint Model Representation

### Posterior Predictive Model

```
θ ~ p(θ)
y ~ p(y | θ)
y^rep ~ p(y | θ)
```

Joint density: p(θ, y, y^rep) = p(θ) · p(y | θ) · p(y^rep | θ)

The posterior p(y^rep, θ | y) is obtained with y observed; posterior predictive draws retain y^rep.

### Prior Predictive Model

```
θ ~ p(θ)
y^rep ~ p(y | θ)
```

Joint density: p(θ, y^rep) = p(θ) · p(y^rep | θ)

### Mixed Replication for Hierarchical Models

```
φ ~ p(φ)
α ~ p(α | φ)
y ~ p(y | α)
α^rep ~ p(α | φ)
y^rep ~ p(y | α^rep)
```

Joint density: p(φ, α, α^rep, y, y^rep) = p(φ) · p(α | φ) · p(y | α) · p(α^rep | φ) · p(y^rep | α^rep)

Only y is observed; φ (hyperparameters) are not replicated.

---

## References

- Bayarri, MJ, and James O Berger. 2000. "P Values for Composite Null Models." *Journal of the American Statistical Association* 95 (452): 1127–42.

- Gabry, Jonah, Daniel Simpson, Aki Vehtari, Michael Betancourt, and Andrew Gelman. 2019. "Visualization in Bayesian Workflow." *Journal of the Royal Statistical Society: Series A (Statistics in Society)* 182 (2): 389–402.

- Gelman, A. 2006. "Prior Distributions for Variance Parameters in Hierarchical Models." *Bayesian Analysis* 1 (3): 515–34.

- Gelman, Andrew, Xiao-Li Meng, and Hal Stern. 1996. "Posterior Predictive Assessment of Model Fitness via Realized Discrepancies." *Statistica Sinica*, 733–60.

- Lunn, David, Christopher Jackson, Nicky Best, Andrew Thomas, and David Spiegelhalter. 2012. *The BUGS Book: A Practical Introduction to Bayesian Analysis*. CRC Press/Chapman & Hall.

- Rubin, Donald B. 1984. "Bayesianly Justifiable and Relevant Frequency Calculations for the Applied Statistician." *The Annals of Statistics*, 1151–72.

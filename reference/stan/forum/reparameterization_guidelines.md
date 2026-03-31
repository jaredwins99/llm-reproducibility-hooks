# Model Reparameterization Guidelines

Source: https://discourse.mc-stan.org/t/are-there-any-general-guidelines-to-aid-model-reparametrization/40788

## Key Principles

**Core Goal**: Reparameterize so the resulting density approximates a standard normal
distribution -- uncorrelated, unit-scaled, centered, with Gaussian tails.

**Main Insight**: "If you can make your parameters uncorrelated and Gaussian shaped
(not thick tailed), derivative-based sampling with finite precision computers will
happily explore."

## General Approaches

### 1. Orthogonalization
Parametrize so the expected Fisher information matrix becomes diagonal, decorrelating
parameters from exponential family distributions.

### 2. Inverse CDF Transformation
Transform from uniform(0,1) distributions using analytic inverse CDFs. Example:
sampling from uniform and applying the Cauchy inverse CDF allows HMC to work with
standard normal distributions internally.

### 3. Centered vs. Non-Centered Parameterization
Effectiveness depends on data informativeness:
- **Non-centered** works better when data is sparse/weakly informative
- **Centered** works better when data is highly informative
- **Mixed** approaches exist for intermediate cases

**Important**: "Parameters can be 'uncoupled' in the prior but still 'coupled' in the
posterior for specific datasets." Posterior geometry matters most for HMC.

## Non-Centered Parameterization Example

```stan
// Centered (can cause funnels with sparse data)
parameters {
  real mu;
  real<lower=0> sigma;
  vector[N] theta;
}
model {
  theta ~ normal(mu, sigma);
}

// Non-centered (avoids funnels)
parameters {
  real mu;
  real<lower=0> sigma;
  vector[N] theta_raw;
}
transformed parameters {
  vector[N] theta = mu + sigma * theta_raw;
}
model {
  theta_raw ~ normal(0, 1);
}
```

## Practical Challenges

Development requires substantial mathematical insight into model-data relationships.
Empirical approaches (examining pairs plots for decorrelation) rarely succeed without
deeper mathematical understanding.

## Recommended Resources

- Stan User's Guide chapters on reparameterization and efficiency tuning
- Betancourt's hierarchical modeling case study
- QR reparameterization for linear models (Stan manual section 9.2)

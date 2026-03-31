# Stan Performance and Sampling Speed Optimization

Sources:
- https://discourse.mc-stan.org/t/how-to-speed-up-sampling-in-rstan/16822
- https://discourse.mc-stan.org/t/how-to-improve-model-sampling-speed-when-applied-to-high-dimension-data/40005
- https://discourse.mc-stan.org/t/how-to-speed-up-my-stan-code-and-sampling-in-rstan/22756

## Implementation Sequence (Priority Order)

### 1. Non-Centered Parameterization (Highest Impact)
Reparameterize random effects for hierarchical models:

```stan
parameters {
  vector[N_groups] effects_raw;
  real<lower=0> sd_effects;
}
transformed parameters {
  vector[N_groups] effects = sd_effects * effects_raw;
}
model {
  effects_raw ~ normal(0, 1);
}
```

### 2. Prior Specification
- Replace uniform priors with regularizing alternatives like `normal(0, 10)`
- Avoid bounds like `uniform(0, 300)` which cause pathological behavior
- Use half-normals for positive-constrained parameters

### 3. Vectorize Calculations
Vectorizing can cut runtime by 30-40%. Use vectorized distribution statements:

```stan
// Slow
for (n in 1:N)
  y[n] ~ normal(mu[n], sigma);

// Fast
y ~ normal(mu, sigma);
```

### 4. Use Sufficient Statistics
When possible, collapse data to sufficient statistics rather than looping over
individual observations.

### 5. Data Structure
Use a long, table-like data structure instead of arrays of matrices for sparse data.

### 6. Compilation Options
- Set `-march=native` for architecture-specific optimization
- Use `STAN_THREADS=true` for within-chain parallelization

### 7. Within-Chain Parallelization
Use `reduce_sum` for parallelizing likelihood computation across observations:

```stan
functions {
  real partial_sum(array[] int y_slice,
                   int start, int end,
                   vector mu, real sigma) {
    return normal_lupdf(to_vector(y_slice) | mu[start:end], sigma);
  }
}
model {
  target += reduce_sum(partial_sum, y, grainsize, mu, sigma);
}
```

### 8. Sampler Settings (Last Resort Only)
Only adjust after structural improvements:
- `adapt_delta`: Increase above 0.8 only if still getting divergences after
  reparameterization
- `max_treedepth`: Increase to 12-15 if hitting tree depth limits (but this
  indicates deeper issues)

## Performance Diagnostics

- Reducing `max_treedepth` from 15 to 10 can dramatically reduce runtime but
  this reflects algorithmic issues needing reparameterization
- Investigate posterior correlations: correlations near 1.0 indicate
  non-identifiability requiring model restructuring
- For large parameter containers, runtime may be dominated by cache misses

## Model Development Strategy

1. Start with the simplest possible model
2. Verify it samples efficiently (zero divergences, no tree depth saturation)
3. Incrementally add complexity
4. At each step, check diagnostics before proceeding

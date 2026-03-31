# Robust Statistical Workflow with PyStan

**Michael Betancourt** | July 2017

Source: https://mc-stan.org/learn-stan/case-studies/pystan_workflow.html

---

**Note**: This case study's content is loaded dynamically via JavaScript and could not be fully scraped. The content below is reconstructed from the RStan workflow companion piece, adapted for PyStan. For the complete original, visit the source URL directly.

## Overview

This case study is the Python/PyStan companion to the RStan workflow guide. It demonstrates the same recommended practices for fitting Bayesian models, emphasizing the importance of validating MCMC diagnostics to ensure accurate posterior estimation, but using PyStan instead of RStan.

## Key Diagnostics (Same as RStan Workflow)

The same five diagnostics apply regardless of interface:

### 1. Split R-hat

Empirically, R-hat > 1.1 is usually indicative of problems in the fit quality across multiple chains.

### 2. Effective Sample Size

When n_eff/n_transitions < 0.001, estimators become biased and overestimate true sample efficiency.

### 3. Tree Depth

Dynamic HMC has maximum trajectory length; saturation indicates insufficient exploration or model specification issues.

### 4. E-BFMI (Energy Bayesian Fraction of Missing Information)

Values below 0.2 suggest inefficient momentum resampling between trajectories.

### 5. Divergences

Indicate pathological posterior regions inadequately explored; real divergences require model reparameterization rather than just increasing adapt_delta.

## PyStan Setup

```python
import pystan
import numpy as np
import matplotlib.pyplot as plt

# Eight Schools data
schools_data = {
    'J': 8,
    'y': [28, 8, -3, 7, -1, 1, 18, 12],
    'sigma': [15, 10, 16, 11, 9, 11, 10, 18]
}
```

## PyStan Model Compilation and Fitting

```python
# Compile model
sm = pystan.StanModel(file='eight_schools_cp.stan')

# Fit model
fit = sm.sampling(data=schools_data, iter=2000, chains=4, seed=194838)

# Print summary
print(fit)
```

## Checking Diagnostics in PyStan

```python
# Extract diagnostics
fit_summary = fit.summary()

# Check for divergences
sampler_params = fit.get_sampler_params(inc_warmup=False)
divergent = [x for y in sampler_params for x in y['divergent__']]
n_divergent = int(sum(divergent))
print(f'{n_divergent} of {len(divergent)} iterations ended with a divergence')

# Check tree depth
treedepth = [x for y in sampler_params for x in y['treedepth__']]
n_max = int(sum([x >= 10 for x in treedepth]))
print(f'{n_max} of {len(treedepth)} iterations saturated the maximum tree depth')

# Check E-BFMI
energy = [y['energy__'] for y in sampler_params]
for chain_energy in energy:
    numer = sum(np.diff(chain_energy)**2) / len(chain_energy)
    denom = np.var(chain_energy)
    if numer / denom < 0.2:
        print('Warning: low E-BFMI detected')
```

## Workflow Recommendations

1. **Modular Organization**: Separate Stan programs, data files, and Python scripts
2. **Reproducibility**: Specify random seeds explicitly
3. **Iterative Refinement**: Increase adapt_delta or reparameterize based on diagnostic results
4. **Visualization**: Use matplotlib/arviz to inspect trace plots and posterior distributions

## Non-Centered Parameterization Solution

The same reparameterization strategy applies as in the RStan workflow:

```stan
data {
  int<lower=0> J;
  real y[J];
  real<lower=0> sigma[J];
}

parameters {
  real mu;
  real<lower=0> tau;
  real theta_tilde[J];
}

transformed parameters {
  real theta[J];
  for (j in 1:J)
    theta[j] = mu + tau * theta_tilde[j];
}

model {
  mu ~ normal(0, 5);
  tau ~ cauchy(0, 5);
  theta_tilde ~ normal(0, 1);
  y ~ normal(theta, sigma);
}
```

See the [RStan Workflow](rstan-workflow.md) for the complete diagnostic walkthrough, which applies identically to PyStan.

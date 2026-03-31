# Survival Models in Stan

## Overview

Survival models address scenarios where an event is certain to occur eventually but is only observed during a limited measurement period. These models apply across contexts from biological organisms to mechanical components.

## Key Model Types

**Parametric Models**: Explicitly model survival time distributions using probability distributions like exponential or Weibull distributions.

**Semi-parametric Models**: Focus on relative covariate effects without fully specifying the baseline hazard function, exemplified by Cox's proportional hazards model.

## Exponential Survival Model

The exponential distribution assumes constant failure risk independent of prior survival duration. If T ~ exponential(lambda), then Pr[T > t] = Pr[T > t + t' | T > t'] (memoryless property).

### Data Structure
- Vector `t` of N observed failure times
- Count of censored observations and censoring time `t_cens`
- Censored items contribute survival function likelihood: Pr[T > t_cens]

### Stan Implementation

```stan
data {
  int<lower=0> N;
  vector[N] t;
  int<lower=0> N_cens;
  real<lower=0> t_cens;
}

parameters {
  real<lower=0> lambda;
}

model {
  t ~ exponential(lambda);
  target += N_cens * exponential_lccdf(t_cens | lambda);
  lambda ~ lognormal(0, 1);
}
```

The lognormal prior suits failure times between 0.1 and 10 time units.

## Weibull Survival Model

The Weibull distribution generalizes the exponential with shape parameter alpha and scale sigma:

$$\text{Weibull}(t \mid \alpha, \sigma) = \frac{\alpha}{\sigma} \left(\frac{t}{\sigma}\right)^{\alpha-1} \exp\left(-\left(\frac{t}{\sigma}\right)^\alpha\right)$$

- When alpha = 1, reduces to exponential distribution
- alpha < 1: Higher early failure probability
- alpha > 1: Lower early failure probability, increasing hazard over time

### Stan Implementation

```stan
parameters {
  real<lower=0> alpha;
  real<lower=0> sigma;
}

model {
  t ~ weibull(alpha, sigma);
  target += N_cens * weibull_lccdf(t_cens | alpha, sigma);

  alpha ~ lognormal(0, 1);
  sigma ~ lognormal(0, 1);
}
```

## Survival with Covariates

Individual-specific rates replace a single global parameter using a log-link generalized linear model:

$$\lambda_n = \exp(x_n \cdot \beta)$$

where x_n represents covariate values and beta contains regression coefficients.

```stan
data {
  int<lower=0> N;
  vector[N] t;
  int<lower=0> N_cens;
  real<lower=0> t_cens;
  int<lower=0> K;
  matrix[N, K] x;
  matrix[N_cens, K] x_cens;
}

parameters {
  vector[K] gamma;
}

model {
  gamma ~ normal(0, 2);
  t ~ exponential(exp(x * gamma));
  target += exponential_lccdf(t_cens | exp(x_cens * gamma));
}
```

## Hazard and Survival Functions

**Survival function**: S(t) = 1 - F_T(t) represents probability of surviving past time t.

**Hazard function**: h(t) = p_T(t)/S(t) represents instantaneous failure risk given survival to time t.

**Cumulative hazard**: H(t) = integral from 0 to t of h(u) du

For exponential distributions, the hazard is constant (h(t) = lambda). For Weibull distributions with alpha > 1, hazard increases over time; with alpha < 1, it decreases.

## Proportional Hazards Model

Cox's semi-parametric model specifies:

$$h(t \mid x_n, \beta) = h_0(t) \cdot \exp(x_n \cdot \beta)$$

The baseline hazard h0(t) remains unmodeled, making this semi-parametric. The model uses a partial likelihood based on failure ordering rather than absolute times.

### Partial Likelihood

For subjects with ordered failure times t1 < t2 < ... < tN:

$$\Pr[n \text{ first to fail among } n, n+1, \ldots, N] = \frac{\exp(x_n \cdot \beta)}{\sum_{n'=n}^{N} \exp(x_{n'} \cdot \beta)}$$

The complete partial likelihood is the product across all observed failures.

### Stan Implementation

```stan
data {
  int<lower=0> K;
  int<lower=0> N;
  vector[N] t;
  matrix[N, K] x;
  int N_c;
  real<lower=t[N]> t_c;
  matrix[N_c, K] x_c;
}

parameters {
  vector[K] beta;
}

model {
  beta ~ normal(0, 2);

  vector[N] log_theta = x * beta;
  vector[N_c] log_theta_c = x_c * beta;
  real log_denom = log_sum_exp(log_theta_c);

  for (n in 1:N) {
    log_denom = log_sum_exp(log_denom, log_theta[n]);
    target += log_theta[n] - log_denom;
  }
}
```

Survival times must be sorted in decreasing order for efficient computation.

## Handling Tied Survival Times

When observed times are identical (common with rounded data), Efron (1977) introduced an approximate partial likelihood that averages contributions across possible orderings.

The Stan implementation uses helper functions to identify unique survival times and applies a more complex likelihood calculation accounting for ties while avoiding intractable permutation enumeration.

---

**References:**
- Breslow (1975): "Analysis of Survival Data Under the Proportional Hazards Model"
- Cox (1972): "Regression Models and Life-Tables"
- Efron (1977): "The Efficiency of Cox's Likelihood Function for Censored Data"
- Plackett (1975): "The Analysis of Permutations"

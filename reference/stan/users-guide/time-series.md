# Time-Series Models

## Overview

The Stan documentation presents comprehensive guidance on implementing time-series models. "Times series data come arranged in temporal order," and the chapter covers regression-like models and hidden Markov approaches.

## Autoregressive Models

### AR(1) Implementation

The foundation uses the relationship: y_n ~ normal(α + β·y_{n-1}, σ). A basic Stan implementation requires three parameters (intercept, slope, noise scale) with a loop starting from observation 2.

For efficiency, vectorized notation replaces loops: "y[2:N] ~ normal(alpha + beta * y[1:(N - 1)], sigma);"

### Stationarity Constraints

To enforce stationary processes, the slope can be bounded: `real<lower=-1, upper=1> beta;` However, the documentation advises: "In practice, such a constraint is not recommended. If the data are not well fit by a stationary model it is best to know this."

### Higher-Order Models

AR(2) extends the approach with two lags. General AR(K) models use arrays and nested loops to compute linear predictors across K previous observations.

## Heteroscedasticity Models

### ARCH(1) Models

These allow noise scale to vary temporally: σ²_t = α₀ + α₁·a²_{t-1}, where a_t represents deviations from mean.

### GARCH(1,1) Models

This extends ARCH with: σ²_t = α₀ + α₁·a²_{t-1} + β₁·σ²_{t-1}

Requirements include: "α₀, α₁, β₁ > 0 and the slopes α₁ + β₁ < 1"

The model uses transformed parameters to compute volatility recursively, then applies vectorized normal distributions.

## Moving Average Models

### MA(Q) Framework

Models use: y_t = μ + θ₁·ε_{t-1} + ... + θ_Q·ε_{t-Q} + ε_t

Error terms are computed in transformed parameters, then used in distribution statements.

### Vectorization Techniques

"A general MA(Q) model with a vectorized distribution statement" handles varying lag counts by using min(t-1, Q) in loops to drop undefined earlier terms.

## ARMA Models

Combining autoregressive and moving-average components, these models track both predictions and errors. The documentation shows that "local variables, such as err in this case, can be reused in Stan."

### Identifiability Issues

MA and ARMA require constraints preventing roots inside the unit circle: `real<lower=-1, upper=1> theta;`

For stationarity: "it's worth adding the following constraint to ensure stationarity: real<lower=-1, upper=1> phi;"

## Stochastic Volatility

These models treat variance as a latent stochastic process with equations:
- y_t = ε_t·exp(h_t/2)
- h_{t+1} = μ + φ(h_t - μ) + δ_t·σ

The documentation notes: "The posterior of a stochastic volatility model such as this one typically has high posterior variance."

### Reparameterization Strategy

Using standardized parameters h_std instead of h dramatically improves mixing. "The reparameterized model reliably converges in tens of iterations."

## Hidden Markov Models

### Framework

These model observations y_{1:N} with discrete hidden states z_{1:N} from {1,...,K}. The likelihood marginalizes states: p(y|φ) = ∫ p(y,z|φ) dz

### Key Components

- **Observation matrix ω**: ω_{kn} = p(y_n | z_n = k, φ)
- **Transition matrix Γ**: Γ_{ij} = p(z_n = j | z_{n-1} = i, φ)
- **Initial state ρ**: typically the stationary distribution

### Stan Functions

The `hmm_marginal` function computes log marginal likelihood. For posterior inference, `hmm_latent_rng` draws from p(z|y,φ) and `hmm_hidden_state_prob` computes state probabilities.

"hmm_hidden_state_prob returns the marginal probabilities of each state, Pr(z_n = k | φ, y)" but should not be used directly for draws due to posterior correlation.

## References

- Engle, R.F. (1982). ARCH with variance estimates
- Kim, S., Shephard, N., & Chib, S. (1998). Stochastic volatility likelihood inference
- Hoffman, M.D., & Gelman, A. (2014). The No-U-Turn Sampler

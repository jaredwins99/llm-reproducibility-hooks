# Diagnosing Biased Inference with Divergences

**Michael Betancourt** | January 2017

Source: https://mc-stan.org/learn-stan/case-studies/divergences_and_bias.html

---

## Introduction to MCMC and Convergence

Markov chain Monte Carlo (MCMC) approximates expectations with respect to a target distribution using chain states. These estimators converge to true expectations asymptotically as chains grow infinitely long. However, practical applications require fast convergence within finite computational budgets.

Fast convergence depends on strong ergodicity conditions, particularly geometric ergodicity between a Markov transition and target distribution. This property ensures estimators follow a central limit theorem, providing both unbiased estimates after finite iterations and empirical precision quantification through MCMC standard error.

## Diagnostic Challenges

Proving geometric ergodicity theoretically proves infeasible for nontrivial problems. Instead, practitioners rely on empirical diagnostics identifying obstructions to proper chain behavior. The split R-hat statistic across multiple chains initialized from diffuse points represents the best general diagnostic, though exploiting specific transition or distribution structures enables better detection.

Hamiltonian Monte Carlo exhibits particular advantages here. Its failures manifest through distinct behaviors converted into sensitive diagnostics. One key behavior involves "divergences" -- these indicate encounters with high-curvature target distribution regions that the chain cannot adequately explore.

## Case Study: Divergences and Hierarchical Models

This analysis demonstrates how divergences signal bias in hierarchical model fitting and reveal underlying pathologies. Alternative model implementations can mitigate these problems through structural changes.

## The Eight Schools Model

The Eight Schools dataset (Rubin 1981) provides a hierarchical model structure:

```
mu ~ N(0, 5)
tau ~ Half-Cauchy(0, 5)
theta_n ~ N(mu, tau)
y_n ~ N(theta_n, sigma_n)
```

Where n in {1, ..., 8} and {y_n, sigma_n} represent observed data.

Inferring hyperparameters mu and tau alongside group-level parameters theta_1, ..., theta_8 enables data pooling and posterior variance reduction. However, this pooling creates challenging geometry obstructing geometric ergodicity and biasing MCMC estimation.

## Centered Parameterization Implementation

The direct centered parameterization implements straightforwardly as a Stan program:

```stan
data {
  int<lower=0> J;
  real y[J];
  real<lower=0> sigma[J];
}

parameters {
  real mu;
  real<lower=0> tau;
  real theta[J];
}

model {
  mu ~ normal(0, 5);
  tau ~ cauchy(0, 5);
  theta ~ normal(mu, tau);
  y ~ normal(theta, sigma);
}
```

Unfortunately, this direct implementation exhibits pathological geometry frustrating geometric ergodicity. Resulting bias proves subtle and may escape detection through standard chain inspection alone.

## Analysis of Short Chains

Initial analysis examines short Markov chains, commonly used when computational resources are limited. R packages facilitate this analysis:

```r
library(rstan)
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())

c_light <- c("#DCBCBC")
c_light_highlight <- c("#C79999")
c_mid <- c("#B97C7C")
c_mid_highlight <- c("#A25050")
c_dark <- c("#8F2727")
c_dark_highlight <- c("#7C0000")
```

Fitting the centered parameterization model with a single short chain:

```r
input_data <- read_rdump("eight_schools.data.R")

fit_cp <- stan(file='eight_schools_cp.stan', data=input_data,
                iter=1200, warmup=500, chains=1, seed=483892929, refresh=1200)
```

Standard diagnostics appear satisfactory initially. The split R-hat shows no problems, and effective sample size per iteration appears reasonable. Trace plots visually seem acceptable.

## Deceptive Diagnostics

Examining the logarithm of tau reveals apparently reasonable exploration of both small and large values. Standard diagnostic summaries show all parameters with R-hat near 1.0 and reasonable effective sample sizes. This apparent adequacy masks underlying problems.

## Key Findings

The centered parameterization creates problematic posterior geometry that divergences can identify before standard diagnostics fail. Divergences represent Hamiltonian dynamics encountering regions where the metric tensor becomes ill-conditioned, preventing proper exploration.

## Non-Centered Parameterization: The Solution

The non-centered parameterization provides a solution by reparameterizing the model to reduce geometric obstructions. This approach maintains identical statistical inference while improving sampler efficiency and eliminating divergences.

### Non-Centered Stan Implementation

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

model {
  mu ~ normal(0, 5);
  tau ~ cauchy(0, 5);
  theta_tilde ~ normal(0, 1);
  y ~ normal(mu + tau * theta_tilde, sigma);
}

generated quantities {
  real theta[J];
  for (j in 1:J)
    theta[j] = mu + tau * theta_tilde[j];
}
```

### Key Differences

The non-centered parameterization separates the hierarchical structure by:
- Introducing standardized parameters `theta_tilde` with unit normal priors
- Constructing the group-level parameters through transformation: `theta = mu + tau * theta_tilde`
- Preserving the same posterior distribution while improving geometric properties

### Practical Benefits

This reformulation eliminates the problematic correlations between hierarchical hyperparameters and group-level estimates. The resulting geometry permits more efficient exploration and prevents the divergences observed in the centered version.

## Practical Implications

Divergences serve as sensitive early warning indicators of geometric pathologies. Practitioners should heed these warnings before relying on chains for inference. When divergences appear, reparameterization efforts -- particularly shifting to non-centered specifications for hierarchical components -- typically resolve issues.

The contrast between centered and non-centered formulations demonstrates how model structure profoundly impacts sampler behavior. Neither parameterization is universally superior; context determines appropriateness. However, for hierarchical models with substantial prior uncertainty on hyperparameters, non-centered approaches generally perform better.

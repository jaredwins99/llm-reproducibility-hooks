# How the Shape of a Weakly Informative Prior Affects Inferences

**Michael Betancourt** | January 2017

Source: https://mc-stan.org/learn-stan/case-studies/weakly_informative_shapes.html

---

## Introduction

Weakly informative priors are an appealing modeling technique where the modeler identifies appropriate scales in a given analysis and uses those scales to introduce principled regularization into the analysis. This case study explores how different implementations of weakly informative priors can produce varying results in Bayesian inference, particularly with sparse data.

## Poorly Informed Regression

### Problem Setup

The analysis examines a scenario where a small company wants to model how daily rainfall affects daily income using only a few measurements. The simulation assumes baseline income of approximately 1 kilodollar daily with rainfall reducing income at a rate of -0.25 k$/cm.

### Data Generation

```r
alpha_true <- 1     # intercept: baseline income in k$
beta_true <- -0.25  # slope: k$ per cm of rain
sigma_true <- 1     # observation noise in k$

set.seed(1234)
N <- 5
x <- runif(N, 0, 2)  # rainfall in cm
y <- rnorm(N, beta_true * x + alpha_true, sigma_true)  # income in k$

stan_rdump(c("N", "x", "y"), file="weakly_informed_regression.data.R")
```

### Model Without Priors (Flat Priors)

```stan
data {
  int<lower=1> N;
  vector[N] x; // Rainfall in cm
  vector[N] y; // Income in k$
}

parameters {
  real alpha;          // k$
  real beta;           // k$ / cm
  real<lower=0> sigma; // k$
}

model {
  y ~ normal(beta * x + alpha, sigma);
}
```

### Results Without Priors

When fitting this model with minimal data and no informative priors, the posterior distribution becomes extremely diffuse and places significant probability on extreme parameter values. The intercept and slope parameters wander far beyond reasonable bounds, with parameter estimates showing substantial uncertainty and implausible ranges.

The posterior means and credible intervals reveal the problem: parameters drift into negative income territory despite theoretical expectations that income should remain positive under most rainfall conditions.

## Two Approaches to Weakly Informative Priors

The case study proposes examining two approaches for implementing weakly informative priors to demonstrate how each affects resulting analyses.

### Approach 1: Scale-Based Priors (Soft Constraints)

This approach uses normal or Cauchy priors centered at reasonable values with scales derived from domain knowledge:

```stan
data {
  int<lower=1> N;
  vector[N] x; // Rainfall in cm
  vector[N] y; // Income in k$
}

parameters {
  real alpha;          // k$
  real beta;           // k$ / cm
  real<lower=0> sigma; // k$
}

model {
  // Weakly informative priors based on domain knowledge:
  // Income is on the order of a few k$ per day
  // Rainfall effect is on the order of k$ per cm
  alpha ~ normal(0, 10);   // Allows wide range but prevents extreme values
  beta ~ normal(0, 5);     // Rainfall effect scale
  sigma ~ cauchy(0, 2.5);  // Half-Cauchy prior on scale

  y ~ normal(beta * x + alpha, sigma);
}
```

The scale-based approach provides soft regularization that gently pulls parameters toward reasonable values without hard boundaries. The normal priors allow the data to overwhelm the prior when data is abundant, while providing meaningful regularization when data is sparse.

### Approach 2: Tighter Domain-Informed Priors

A more targeted approach incorporates tighter domain knowledge:

```stan
data {
  int<lower=1> N;
  vector[N] x; // Rainfall in cm
  vector[N] y; // Income in k$
}

parameters {
  real alpha;          // k$
  real beta;           // k$ / cm
  real<lower=0> sigma; // k$
}

model {
  // Tighter priors from domain knowledge:
  // Baseline income is ~1 k$ with uncertainty
  // Rain reduces income but not dramatically
  alpha ~ normal(1, 1);     // Baseline income around 1 k$
  beta ~ normal(0, 0.5);    // Modest rainfall effect
  sigma ~ normal(0, 1);     // Observation noise scale

  y ~ normal(beta * x + alpha, sigma);
}
```

## Key Insights

### Prior Shape Matters, Not Just Scale

The central insight is that the _shape_ of how priors incorporate domain knowledge -- through their functional form rather than just their scale -- substantively affects inference quality and posterior behavior. Two priors with the same nominal "weakness" (both being "weakly informative") can produce substantially different posteriors when data is sparse.

### When Priors Matter Most

Weakly informative priors are especially critical when inferences are hindered with only weakly identifiable likelihoods, particularly with sparse datasets. In these regimes:

1. **Flat priors** lead to diffuse, uninformative posteriors that place probability on implausible parameter values
2. **Overly vague "weakly informative" priors** may not provide enough regularization
3. **Well-calibrated weakly informative priors** based on domain knowledge provide principled regularization preventing implausible inferences

### Practical Guidelines

1. **Identify the scales**: Determine the natural scales of your parameters (units, order of magnitude)
2. **Use domain knowledge**: Even rough knowledge ("income is positive", "effect is small") is valuable
3. **Prior predictive simulation**: Sample from the prior and check if implied data is reasonable
4. **Sensitivity analysis**: Compare posteriors under different reasonable priors
5. **Document your reasoning**: Record why you chose specific prior distributions and scales

## Connection to Regularization

The case study demonstrates that thoughtful specification of prior scales -- derived from domain knowledge about rainfall and income magnitudes -- provides principled regularization preventing implausible inferences from sparse datasets. This Bayesian regularization has a direct connection to frequentist penalized regression:

- Normal priors correspond to L2 (ridge) regularization
- Laplace priors correspond to L1 (lasso) regularization
- Horseshoe and similar priors correspond to more sophisticated sparsity-inducing penalties

The Bayesian framework, however, provides a principled basis for choosing the regularization strength through domain expertise rather than cross-validation.

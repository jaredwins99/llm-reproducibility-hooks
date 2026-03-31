# Problematic Posteriors

## Overview

The page discusses issues in Bayesian models that create problematic posterior inferences. Even mathematically sound posteriors can be ill-behaved in practice, creating challenges for both sampling and inference.

## Collinearity of Predictors in Regressions

### Examples of Collinearity

#### Redundant Intercepts

Consider observations y_n with two intercept parameters λ₁ and λ₂, scale parameter σ > 0, and data model:

```
y_n ~ normal(λ₁ + λ₂, σ)
```

The sampling density remains unchanged when adding constant q to λ₁ while subtracting it from λ₂. An improper uniform prior p(μ,σ) ∝ 1 leads to an improper posterior. The sampler must spend equal time at λ₁=1,000,000,000 and λ₂=-1,000,000,000 as at λ₁=0 and λ₂=0.

The marginal posterior p(λ₁,λ₂ | y) is improper, appearing as a ridge where λ₂ = λ₁ + c.

#### Ability and Difficulty in IRT Models

In item-response theory with student abilities αⱼ and item difficulties βᵢ:

```
y_{i,j} ~ Bernoulli(logit⁻¹(αⱼ - βᵢ))
```

For any constant c, adding c to all abilities and subtracting from all difficulties produces identical probabilities. This creates a multivariate ridge similar to the redundant intercept problem.

#### General Collinear Regression Predictors

In linear regression y_n ~ normal(x_n β, σ), if column k of the predictor matrix equals c times column k', the coefficients can covary without changing predictions:

```
p(y | ..., β_k, ..., β_{k'}, ..., σ) = p(y | ..., d β_k, ..., d/c β_{k'}, ..., σ)
```

Even nearly collinear predictors cause similar inference problems.

#### Multiplicative Issues with IRT Discrimination

Adding discrimination parameters δᵢ:

```
y_{i,j} ~ Bernoulli(logit⁻¹(δᵢ(αⱼ - βᵢ)))
```

Multiplying δ by c and dividing α and β by c produces the same likelihood. If c < 0, this switches all signs without changing density.

#### Softmax with K vs. K-1 Parameters

The softmax function maps a K-vector α to a K-simplex θ:

```
θ_k = exp(α_k) / Σ_{k'=1}^K exp(α_{k'})
```

This function is many-to-one: adding or subtracting a constant from each αₖ produces the same simplex θ. This causes lack of identifiability in unconstrained parameters.

### Mitigating the Invariances

#### Removing Redundant Parameters or Predictors

The simplest solution is removal. For multiple intercepts, use single intercept parameter μ with y_n ~ normal(μ, σ). For collinear predictors, remove redundant columns from the predictor matrix.

#### Pinning Parameters

For IRT models, fix the first student ability α₁ = 0, allowing all others to be interpreted relative to student 1. For multiplicative invariance with discrimination, pin δ₁ = 1. For softmax, pin αₖ = 0.

Stan code example for simplex creation:
```stan
vector softmax_id(vector alpha) {
  vector[num_elements(alpha) + 1] alphac1;
  for (k in 1:num_elements(alpha)) {
    alphac1[k] = alpha[k];
  }
  alphac1[num_elements(alphac1)] = 0;
  return softmax(alphac1);
}
```

#### Adding Priors

Imposing proper priors resolves invariance problems. For example, normal priors on multiple intercepts:

```
λ₁, λ₂ ~ normal(0, τ)
```

ensure the posterior mode is at λ₁ = λ₂, minimizing the log prior density.

The page shows three posteriors: two intercepts with improper prior (ridge extending infinitely), two intercepts with standard normal prior (proper posterior), and single intercept with improper prior (proper posterior).

#### Vague, Strongly Informative, and Weakly Informative Priors

Too broad (vague) priors theoretically resolve issues but samplers still struggle practically. Ideally, substantive knowledge informs realistic priors. Weakly informative priors balance computational control without dominating data. Modelers should understand expected estimate scales to choose appropriately.

## Label Switching in Mixture Models

Where collinearity creates infinitely many posterior maxima, component swapping in mixture models creates finitely many.

### Mixture Models

Consider a normal mixture with locations μ₁ and μ₂, shared scale σ > 0, mixture ratio θ ∈ [0,1]:

```
p(y | θ, μ₁, μ₂, σ) = ∏_{n=1}^N (θ normal(y_n | μ₁, σ) + (1-θ) normal(y_n | μ₂, σ))
```

Exchangeability of components means:
```
p(θ, μ₁, μ₂, σ | y) = p((1-θ), μ₂, μ₁, σ | y)
```

With K components, K! identical posterior maxima exist.

### Convergence Monitoring and Effective Sample Size

Label switching compromises the R-hat convergence statistic and effective sample size calculations, both dependent on posterior means. The posterior mean for μ₁ equals μ₂, and θ's posterior mean is always 1/2 regardless of data.

### Some Inferences Are Invariant

Posterior predictive inferences are invariant to label switching; log probability of new observations doesn't depend on component identities. Only inferences invariant to label switching are sound. Posterior means for parameters are meaningless due to non-invariance.

### Highly Multimodal Posteriors

While theoretically sound, balancing exploration of multiple local maxima is computationally intractable. Gibbs sampling struggles when sampled parameters must move to new modes. HMC and NUTS get stuck in one "bowl" around modes without gathering sufficient energy to escape. With increasing components, modal growth becomes super-exponential, making all known sampling techniques ineffective.

### Hacks as Fixes

#### Parameter Ordering Constraints

Constraining μ₁ < μ₂ identifies components but causes problems when substantial probability mass supports μ₁ > μ₂. Posterior uncertainty isn't captured, and event probability estimation fails. For instance:

```
Pr[μ₁ > μ₂] ≈ Σ_{m=1}^M I(μ₁^{(m)} > μ₂^{(m)})
```

estimates zero because the posterior respects the constraint.

#### Initialization Around a Single Mode

Running single chains or initializing near realistic values works better if reasonable values exist and labels don't switch within chains. All chains remain glued to one modal neighborhood.

## Component Collapsing in Mixture Models

Two mixture components can collapse to identical values: μᵢ = μⱼ and σᵢ = σⱼ for i ≠ j. This typically happens early during initialization or MCMC. Once parameters match, escaping the low-density trough between current values and non-collapsed ones becomes difficult.

Helpful measures include: smaller step sizes during warmup, stronger priors on component membership responsibility, or adding extra components accepting some may collapse.

Recovering exactly the right K mixture components is difficult as K increases beyond one.

## Posteriors with Unbounded Densities

Posterior density grows without bounds as parameters approach certain poles or boundaries, creating no posterior modes and numerical stability issues.

### Mixture Models with Varying Scales

With scales σ₁ and σ₂ for locations μ₁ and μ₂, density grows unbounded as σ₁ → 0 and μ₁ → y_n for some data point n. One mixture component concentrates all mass around a single observation.

### Beta-Binomial Models with Skewed Data and Weak Priors

A posterior like beta(φ | 0.5, 0.5) is unbounded as φ → 0 and φ → 1. With Bernoulli data and weak beta prior:

```
p(φ | y) ∝ beta(φ | 0.5, 0.5) × ∏_{n=1}^N Bernoulli(y_n | φ)
         = beta(φ | 0.5 + Σ y_n, 0.5 + N - Σ y_n)
```

With N=9 and all y_n=1, the posterior is beta(φ | 9.5, 0.5), unbounded as φ → 1. Despite being improper in the bounded sense, the posterior is proper and the posterior mean equals exactly 0.95.

#### Constrained vs. Unconstrained Scales

Stan doesn't sample directly on constrained (0,1) space. Probability values φ are logit-transformed to (-∞, ∞), pushing boundaries to ±∞. The automatic Jacobian adjustment ensures unconstrained density propriety. For (0,1), the adjustment is:

```
log logit⁻¹(φ) + log logit(1 - φ)
```

Two problems remain: if posterior mass concentrates near boundaries, logit-transformed parameters sweep long paths dominating U-turn conditions; inverse transformation can underflow to 0 or overflow to 1 even with finite unconstrained parameters.

## Posteriors with Unbounded Parameters

Posterior density doesn't grow unbounded, but parameters grow unbounded with gradually increasing density, creating no posterior modes.

### Separability in Logistic Regression

With logistic regression, N outcomes y_n ∈ {0,1}, N×K predictor matrix x, K-dimensional coefficient vector β:

```
y_n ~ Bernoulli(logit⁻¹(x_n β))
```

If column k satisfies x_{n,k} > 0 if and only if y_n = 1 (separability), predictive accuracy improves as β_k → ∞. For cases with y_n = 1, x_n β → ∞ and logit⁻¹(x_n β) → 1.

No likelihood maximum exists, so no maximum likelihood estimate. The posterior is improper and the marginal posterior mean for β_k is undefined. The Bayesian solution is a proper prior ensuring a proper posterior.

## Uniform Posteriors

With parameter ψ ∈ [0,1] and flat prior uniform(ψ | 0,1), if data contain no information about ψ, the posterior is also uniform(ψ | 0,1).

Although no maximum likelihood estimate exists, the uniform posterior on [0,1] is proper. The posterior mean for ψ is well-defined: 1/2. Despite lacking a posterior mode, posterior predictive inference integrates over all [0,1] points.

## Sampling Difficulties with Problematic Priors

With improper posteriors, proper posterior exploration is theoretically impossible. However, Gibbs sampling (BUGS/JAGS) behaves differently than Hamiltonian Monte Carlo (Stan) when faced with unidentified models.

### Gibbs Sampling

Gibbs sampling may appear efficient for unidentified models but doesn't properly explore the posterior. With initial values λ₁^{(0)}, λ₂^{(0)}, iteration m draws:

```
λ₁^{(m)} ~ p(λ₁ | λ₂^{(m-1)}, σ^{(m-1)}, y)
λ₂^{(m)} ~ p(λ₂ | λ₁^{(m)}, σ^{(m-1)}, y)
σ^{(m)} ~ p(σ | λ₁^{(m)}, λ₂^{(m)}, y)
```

The next λ₁ draw range is highly constrained by current λ₂ and σ values. Gibbs runs quickly providing seemingly reasonable inferences for λ₁ + λ₂ but doesn't explore the full posterior—it takes a slow random walk from initial values. This random walk behavior explains preference for Hamiltonian Monte Carlo when parameters are posterior-correlated.

### Hamiltonian Monte Carlo Sampling

HMC explores correlated posteriors more efficiently. The Hamiltonian dynamics (fictitious particle motion in the negative log posterior field) run up and down the valley defined by potential energy (posterior ridges correspond to potential energy valleys). With random momentum for λ₁ and λ₂, the gradient adjusts for correlation, running parameters in opposite directions along the ridge valley.

### No-U-Turn Sampling

Stan's default no-U-turn sampler (NUTS) explores posteriors even more efficiently. NUTS simulates particle motion until a U-turn occurs. With improper posteriors, the sampler moves indefinitely down the potential valley without U-turning. In practice, the maximum leapfrog step limit hits in many iterations, causing large numbers of probability and gradient evaluations (1000 with default max tree depth of 10). Slow sampling indicates an improper posterior, not an algorithmic bug. It's impossible to sample from improper posteriors.

### Examples: Fits in Stan

Three models with increasing parameter identification were fit with default parameters (1000 warmup, 1000 sampling iterations, NUTS with max tree depth 10) to N=100 data points from y_n ~ normal(0,1):

**Two Scale Parameters, Improper Prior**
```stan
data {
  int N;
  array[N] real y;
}
parameters {
  real lambda1;
  real lambda2;
  real<lower=0> sigma;
}
transformed parameters {
  real mu;
  mu = lambda1 + lambda2;
}
model {
  y ~ normal(mu, sigma);
}
```

Results show:
- lp__: -5.3e+01 (Mean: -5.3e+01)
- n_leapfrog__: 1.4e+03 (high values indicate problems)
- lambda1: Mean 1.3e+03, 95% interval (-2.3e+03, 6.0e+03)
- lambda2: Mean -1.3e+03, 95% interval (-6.0e+03, 2.3e+03)
- sigma: 1.0e+00
- mu: 1.6e-01
- R_hat > 1.0 for lambda1 and lambda2 (non-convergence)

**Two Scale Parameters, Weak Prior**

Adding to model block:
```stan
lambda1 ~ normal(0, 10);
lambda2 ~ normal(0, 10);
```

Results show:
- lp__: -54
- n_leapfrog__: 157 (much lower)
- lambda1: Mean 0.31, 95% interval (-12, 12)
- lambda2: Mean -0.14, 95% interval (-12, 12)
- sigma: 1.0
- mu: 0.16
- R_hat near 1.0 (convergence)

**One Scale Parameter, Improper Prior**

Single location parameter model:
```stan
data {
  int N;
  array[N] real y;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  y ~ normal(mu, sigma);
}
```

Results show:
- lp__: -54
- n_leapfrog__: 3.2 (very low)
- mu: Mean 0.17, 95% interval (-3.8e-03, 0.33)
- sigma: 1.0
- R_hat near 1.0 (convergence)

Key observations across models:
- Only non-identified model shows non-convergent R_hat for problematic parameters
- Average leapfrog steps: ~3 (identified), ~150 (weakly identified), ~1400 (non-identified)
- Effective sample size per second: ~31,000 (identified), ~1,900 (weakly identified), ~200 (non-identified)
- True μ=0 and σ=1 fall within 90% posterior intervals in all models
- Lack of convergence and max leapfrog step hitting clearly indicate improper posteriors
- HMC's clear failure provides better diagnostics than Gibbs sampling might

## References

Hoffman, Matthew D., and Andrew Gelman. 2014. "The No-U-Turn Sampler: Adaptively Setting Path Lengths in Hamiltonian Monte Carlo." Journal of Machine Learning Research 15: 1593-623.

Neal, Radford M. 1996. "Sampling from Multimodal Distributions Using Tempered Transitions." Statistics and Computing 6 (4): 353-66.

Swendsen, Robert H., and Jian-Sheng Wang. 1986. "Replica Monte Carlo Simulation of Spin Glasses." Physical Review Letters 57: 2607-9.

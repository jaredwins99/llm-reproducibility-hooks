# Robust Statistical Workflow with RStan

**Michael Betancourt** | July 2017

Source: https://mc-stan.org/learn-stan/case-studies/rstan_workflow.html

---

## Introduction

Stan is a powerful tool for specifying and fitting complex Bayesian models through dynamic Hamiltonian Monte Carlo. However, power must be paired with responsibility. While dynamic implementations of HMC perform well across many models, success is not guaranteed. When failures occur, they manifest in diagnostics that can be readily identified and addressed.

By acknowledging these diagnostics, practitioners can ensure accurate posterior fitting and proper model characterization.

## A Little Bit About Markov Chain Monte Carlo

Hamiltonian Monte Carlo implements Markov chain Monte Carlo (MCMC), an algorithm approximating expectations with respect to a target distribution pi through Markov chain states.

The estimator is:

    E_pi[f] approx f_hat_N = (1 / (N + 1)) * sum_{n=0}^{N} f(q_n)

These estimators are guaranteed accurate only asymptotically as chain length approaches infinity:

    lim_{N -> inf} f_hat_N = E_pi[f]

For practical utility, fast convergence requires strong ergodicity conditions, specifically geometric ergodicity. This ensures MCMC estimators follow a central limit theorem, providing unbiased estimates and empirical precision quantification:

    f_hat_N - E_pi[f] ~ N(0, sqrt(Var[f] / N_eff))

Proving geometric ergodicity theoretically is infeasible for nontrivial problems. Instead, practitioners rely on empirical diagnostics identifying obstructions to geometric ergodicity. The split R-hat statistic across multiple chains provides the best general diagnostic.

HMC offers particular advantages through structure-specific diagnostics. Divergences indicate regions of high curvature the sampler cannot adequately explore. The energy Bayesian fraction of missing information (E-BFMI) quantifies momentum resampling efficacy between trajectories.

## Setting Up The RStan Environment

Begin by loading RStan and configuring local options:

```r
library(rstan)
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())
```

Setting `rstan_options(auto_write = TRUE)` enables caching compiled models for repeated runs without recompilation overhead. The `options(mc.cores = parallel::detectCores())` setting enables parallel execution across available processor cores.

These settings are recommended for local machines with adequate RAM. Very large problems may exhaust memory when running chains in parallel, warranting disabled parallelization.

Load utility functions for diagnostic checking:

```r
source('stan_utility.R')
lsf.str()

# check_div : function (fit)
# check_energy : function (fit)
# check_treedepth : function (fit, max_depth = 10)
# count_divergences : function (fit)
# hist_treedepth : function (fit)
# partition_div : function (fit)
```

## Specifying and Fitting A Model in Stan

Consider a hierarchical model of the eight schools dataset:

    mu ~ N(0, 5)
    tau ~ Half-Cauchy(0, 5)
    theta_n ~ N(mu, tau)
    y_n ~ N(theta_n, sigma_n)

where n in {1, ..., 8} and {y_n, sigma_n} are observed data.

### Specifying the Model with a Stan Program

Implement the centered parameterization, known to challenge sophisticated samplers:

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

Maintain modularity by separating Stan programs into distinct files from the R environment.

### Specifying the Data

Similarly, maintain separate data files:

```r
J <- 8
y <- c(28,  8, -3,  7, -1,  1, 18, 12)
sigma <- c(15, 10, 16, 11,  9, 11, 10, 18)

stan_rdump(c("J", "y", "sigma"), file="eight_schools.data.R")
```

Read existing Stan data files using:

```r
data <- read_rdump("eight_schools.data.R")
```

### Fitting the Model

Run Stan with explicit seed specification for reproducibility:

```r
fit <- stan(file='eight_schools_cp.stan', data=data, seed=194838)
```

By default, the sampling method runs 4 Markov chains initialized from diffuse points, each with 1000 warmup and 1000 sampling iterations, totaling 4000 available post-warmup draws. Parallel execution occurs when configured.

## Validating a Fit in Stan

### Checking Split R-hat and Effective Sample Sizes

Display universal MCMC diagnostics using the print method:

```r
print(fit)
```

```
Inference for Stan model: eight_schools_cp.
4 chains, each with iter=2000; warmup=1000; thin=1;
post-warmup draws per chain=1000, total post-warmup draws=4000.

           mean se_mean   sd   2.5%    25%    50%    75% 97.5% n_eff Rhat
mu         4.50    0.18 3.45  -2.09   2.18   4.52   6.76 11.87   367 1.01
tau        4.29    0.19 3.34   0.60   1.95   3.36   5.62 13.27   321 1.01
theta[1]   6.77    0.19 5.94  -3.09   3.16   6.10   9.69 20.95   980 1.00
theta[2]   5.21    0.17 5.13  -4.58   2.05   5.41   8.07 15.43   915 1.00
theta[3]   3.89    0.21 5.88  -9.51   0.66   4.26   7.25 14.69   760 1.00
theta[4]   4.91    0.17 5.05  -5.20   1.68   4.96   7.88 15.00   922 1.00
theta[5]   3.57    0.18 5.03  -6.99   0.41   3.92   6.87 12.73   783 1.00
theta[6]   4.07    0.18 5.22  -6.87   0.86   4.43   7.36 13.56   845 1.00
theta[7]   6.83    0.18 5.34  -2.70   3.30   6.52   9.84 18.54   880 1.00
theta[8]   5.15    0.16 5.92  -6.44   1.63   5.12   8.24 17.29  1319 1.00
lp__     -16.11    0.44 5.81 -27.19 -20.05 -16.29 -12.05 -5.27   172 1.01
```

Ensure split R-hat values approach 1.0; values exceeding 1.1 typically indicate fitting problems. Here all parameters show acceptable values.

Examine effective sample size (n_eff). When `n_eff / n_transitions < 0.001`, estimators become biased and may significantly overestimate true effective sample size.

Both elevated split R-hat and low effective samples per transition reflect poorly mixing chains. Improving mixing typically requires model reparameterization or stronger priors.

### Checking the Tree Depth

Stan's dynamic HMC implementation has a maximum trajectory length preventing infinite loops for non-identified models. Complex identified models may saturate this threshold, limiting sampler efficacy.

Check saturation using utility functions:

```r
check_treedepth(fit)
# [1] "0 of 4000 iterations saturated the maximum tree depth of 10 (0%)"
```

For saturated thresholds, rerun with larger maximum tree depth:

```r
fit <- stan(file='eight_schools_cp.stan', data=data, seed=194838,
            control=list(max_treedepth=15))
```

### Checking the E-BFMI

Hamiltonian Monte Carlo proceeds in two phases: trajectory simulation exploring parameter space, followed by momentum resampling enabling exploration of new regions. Short jumps between slices due to poor momentum resampling indicate slow exploration.

Identify this problem through energy Bayesian Fraction of Missing Information:

```r
check_energy(fit)
```

The `check_energy` function uses a 0.2 threshold based on preliminary empirical studies. This represents a rough recommendation requiring refinement through broader application.

Problems indicated by low E-BFMI, like split R-hat and low effective samples, require model specification adjustments. Solutions depend on specific model structure and lack generic approaches.

### Checking Divergences

Divergences indicate pathological posterior neighborhoods where simulated trajectories cannot adequately explore. This fit exhibits significant divergences:

```r
check_div(fit)
# [1] "126 of 4000 iterations ended with a divergence (3.15%)"
# [1] "Try running with larger adapt_delta to remove the divergences"
```

This indicates incomplete posterior exploration and biased MCMC estimators.

Divergences may constitute false positives. Verify genuine fitting issues by rerunning with larger target acceptance probability `adapt_delta`, forcing more accurate trajectory simulation:

```r
fit <- stan(file='eight_schools_cp.stan', data=data, seed=194838,
            control=list(adapt_delta=0.90))
```

Check again:

```r
check_div(fit)
# [1] "52 of 4000 iterations ended with a divergence (1.3%)"
# [1] "Try running with larger adapt_delta to remove the divergences"
```

Divergences decreased but did not vanish. Complete elimination requires adapt_delta sufficiently close to 1.0.

### Analyzing Divergences Graphically

If the divergences are not false positives then they will tend to concentrate in the pathological neighborhoods of the posterior.

```r
c_dark <- c("#8F272780")
green <- c("#00FF0080")

partition <- partition_div(fit)
div_params <- partition[[1]]
nondiv_params <- partition[[2]]

par(mar = c(4, 4, 0.5, 0.5))
plot(nondiv_params$'theta[1]', log(nondiv_params$tau),
     col=c_dark, pch=16, cex=0.8, xlab="theta[1]", ylab="log(tau)",
     xlim=c(-20, 50), ylim=c(-1,4))
points(div_params$'theta[1]', log(div_params$tau),
       col=green, pch=16, cex=0.8)
```

The visualization reveals that divergences cluster in specific parameter regions (at small values of tau) rather than dispersing randomly, confirming genuine fitting problems rather than false positives.

## Reparameterization Solution

The centered parameterization proves problematic because the hierarchical structure creates challenging posterior geometry. The solution involves implementing a non-centered parameterization that decorrelates the parameters.

### Non-Centered Parameterization Stan Model

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

The key difference: instead of directly modeling `theta`, we model centered deviations `theta_tilde` and construct the actual parameters through a transformation. This approach dramatically improves sampler efficiency.

### Fitting with Reparameterization

```r
fit_nc <- stan(file='eight_schools_nc.stan', data=data, seed=194838)

print(fit_nc)
check_div(fit_nc)
check_energy(fit_nc)
check_treedepth(fit_nc)
```

The results demonstrate substantial improvement. Divergences vanish, effective sample sizes increase significantly, and energy diagnostics improve, confirming that the reparameterization successfully resolved the pathological geometry.

## Key Takeaways: Diagnostic Workflow Summary

1. **Split R-hat**: Ensure all values < 1.1. Higher values indicate chains exploring different regions.
2. **Effective sample size**: Check n_eff/n_transitions > 0.001 for all parameters.
3. **Tree depth**: Check for saturation at maximum tree depth. Increase max_treedepth if needed.
4. **E-BFMI**: Check all chains have E-BFMI > 0.2. Low values indicate poor momentum resampling.
5. **Divergences**: Any divergences indicate potential bias. Try increasing adapt_delta first; if they persist, reparameterize the model.

The workflow emphasizes that Stan's diagnostics provide actionable guidance for model improvement. Rather than accepting problematic fits, practitioners should iteratively refine model specifications, particularly through reparameterization strategies that exploit problem structure.

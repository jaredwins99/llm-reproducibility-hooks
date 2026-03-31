# Identifying Bayesian Mixture Models

**Michael Betancourt** | February 2017

Source: https://mc-stan.org/learn-stan/case-studies/identifying_mixture_models.html

---

Mixture modeling is a powerful technique for integrating multiple data generating processes into a single model. Unfortunately when those data generating processes are degenerate the resulting mixture model suffers from inherent combinatorial non-identifiabilities that frustrate accurate computation. Consequently, in order to utilize mixture models reliably in practice we need strong and principled prior information to ameliorate these frustrations.

In this case study I will first introduce how mixture models are implemented in Bayesian inference. I will then discuss the non-identifiability inherent to that construction as well as how the non-identifiability can be tempered with principled prior information. Lastly I will demonstrate how these issues manifest in a simple example, with a final tangent to consider an additional pathology that can arise in Bayesian mixture models.

## Mixture Models

In a mixture model we assume that a given measurement, y, can be drawn from one of K data generating processes, each with their own set of parameters, pi_k(y | alpha_k). To implement such a model we need to construct the corresponding likelihood and then subsequent posterior distribution.

### The Mixture Likelihood

Let z in {0, ..., K} be an _assignment_ that indicates to which data generating process our measurement was generated. Conditioned on this assignment, the mixture likelihood is just

    pi(y | alpha, z) = pi_z(y | alpha_z),

where alpha = (alpha_1, ..., alpha_K).

By combining assignments with a set of data generating processes we admit an extremely expressive class of models that encompass many different inferential and decision problems. For example, if multiple measurements y_n are given but the corresponding assignments z_n are unknown then inference over the mixture model is equivalent to _clustering_ the measurements across the component data generating processes. Similarly, if both the measurements and the assignments are given then inference over the mixture model admits _classification_ of future measurements. Finally, _semi-supervised_ learning corresponds to inference over a mixture model where only some of the assignments are known.

In practice discrete assignments are difficult to fit accurately and efficiently, but we can facilitate inference by _marginalizing_ the assignments out of the model entirely. If each component in the mixture occurs with probability theta_k,

    theta = (theta_1, ..., theta_K), 0 <= theta_k <= 1, sum_{k=1}^{K} theta_k = 1,

then the assignments follow a multinomial distribution,

    pi(z | theta) = theta_z,

and the joint likelihood over the measurement and its assignment is given by

    pi(y, z | alpha, theta) = pi(y | alpha, z) * pi(z | theta) = pi_z(y | alpha_z) * theta_z.

Marginalizing over all of the possible assignments then gives

    pi(y | alpha, theta) = sum_{z} pi(y, z | alpha, theta)
                         = sum_{z} pi_z(y | alpha_z) * theta_z
                         = sum_{k=1}^{K} pi_k(y | alpha_k) * theta_k
                         = sum_{k=1}^{K} theta_k * pi_k(y | alpha_k).

In words, after marginalizing out the assignments the mixture likelihood reduces to a convex combination of the component data generating processes.

Marginalizing out the discrete assignments yields a likelihood that depends on only continuous parameters, making it amenable to state-of-the-art tools like Stan. Moreover, modeling the latent mixture probabilities instead of the discrete assignments admits more precise inferences as a consequence of the Rao-Blackwell theorem. From any perspective the marginalized mixture likelihood is the ideal basis for inference.

### Bayesian Mixture Posteriors

In order to perform Bayesian inference over a mixture model we need to complement the mixture likelihood with prior distributions for both the component parameters, alpha, and the mixture probabilities, theta. Assuming that these distributions are independent a priori,

    pi(alpha, theta) = pi(alpha) * pi(theta),

the subsequent posterior for a single measurement takes the form

    pi(alpha, theta | y) proportional to pi(alpha) * pi(theta) * sum_{k=1}^{K} theta_k * pi_k(y | alpha_k).

Similarly, the posterior for multiple measurements becomes

    pi(alpha, theta | y) proportional to pi(alpha) * pi(theta) * sum_{n=1}^{N} sum_{k=1}^{K} theta_k * pi_k(y_n | alpha_k).

Additional measurements, however, do not impact the non-identifiability inherent to mixture models. Consequently we will consider only a single measurement in the proceeding section, returning to multiple measurements in the example.

## Degenerate Mixture Models and Non-identifiability

When making inferences with a mixture model we need to learn each of the component weights, theta_k, and the component parameters, alpha_k. This introduces a subtle challenge because if the measurement cannot discriminate between the components then it cannot discriminate between the component parameters.

If the individual component distributions pi_k(y | alpha_k) are distinct then the unique characteristics of each can be enough to inform the corresponding parameters individually and the mixture model is straightforward to fit. Circumstances become much more dire, however, in the _degenerate_ case when the components are identical, pi_k(y | alpha_k) = pi(y | alpha_k). In this case there is a fundamental ambiguity as to which parameters alpha_k are associated with each component in the mixture.

To see this, let sigma denote a permutation of the indices in our mixture,

    sigma(1, ..., K) -> (sigma(1), ..., sigma(K)),

with

    sigma(alpha) = sigma(alpha_1, ..., alpha_K) -> (alpha_{sigma(1)}, ..., alpha_{sigma(K)}).

When the component distributions are identical the mixture likelihood is invariant to any permutation of the indices,

    pi(y | sigma(alpha), sigma(theta)) = sum_{k=1}^{K} theta_{sigma(k)} * pi_{sigma(k)}(y | alpha_{sigma(k)})
                                        = sum_{k'=1}^{K} theta_{k'} * pi_{k'}(y | alpha_{k'})
                                        = pi(y | alpha, theta).

Moreover, when the priors are _exchangeable_, pi(sigma(alpha)) = pi(alpha) and pi(sigma(theta)) = pi(theta), then the posterior will inherit the permutation invariance of the mixture likelihood. In this case all of our inferences will be the same regardless of how we label the mixture components with explicit indices.

Because of this labeling degeneracy the posterior distribution will be non-identified. In particular, it will manifest multimodality, with one mode for each of the possible labelings. For a mixture with K identical components there are K! possible labelings and hence any degenerate mixture model will exhibit at least K! modes.

Hence even for a relatively small number of components the posterior distribution will have too many modes for any statistical algorithm to accurately quantify unless the modes collapse into each other. For example, if we applied Markov chain Monte Carlo then any chain would be able to explore one of the modes but it would not be able to transition _between_ the modes, at least not within in any finite running time.

## Identifying Degenerate Bayesian Mixture Models

Even if we had a statistical algorithm that could transition between the degenerate modes and explore the entire mixture posterior, typically there will be too many modes to complete that exploration in any reasonable time. Consequently if we want to accurately fit these models in practice then we need to break the labeling degeneracy and remove the extreme multimodality altogether.

Exactly how we break the labeling degeneracy depends on what prior information we can exploit. In particular, our strategy will be different depending on whether our prior information is exchangeable or not.

### Identification with Non-exchangeable Prior Information

Because the posterior distribution inherits the permutation-invariance of the mixture likelihood only if the priors are exchangeable, one way to immediately obstruct the labeling degeneracy of the mixture posterior is to employ non-exchangeable priors. This approach is especially useful when each component of the likelihood is meant to be responsible for a specific purpose, for example when each component models a known subpopulation with distinct behaviors about which we have prior information. If this principled prior information is strong enough then the prior can suppress all but the one labeling consistent with these responsibilities, ensuring a unimodal mixture posterior distribution.

### Identification with Exchangeable Prior Information

When our prior information is exchangeable there is nothing preventing the mixture posterior from becoming multimodal and impractical to fit. When our inferences are also exchangeable, however, we can exploit the symmetry of the labeling degeneracies to simplify the computational problem dramatically.

#### The Geometry of a Degenerate Posterior

Each labeling is characterized by the unique assignment of indices to the components in our mixture. Permuting the indices yields a new assignment and hence a new labeling of our mixture model. Consequently a natural way to identify each labeling is to choose a standard set of indices, alpha_1, ..., alpha_K, and distinguish each labeling by the permutation that maps to the appropriate indices, alpha_{sigma(1)}, ..., alpha_{sigma(K)}. The standard indices themselves identify a labeling with the trivial permutation that leaves the indices unchanged.

In general it is difficult to utilize these permutations, but if the component parameters, alpha_n, are scalar then we can exploit their unique _ordering_ to readily identify permutations and hence labelings. For example, if we choose the standard labeling to be the one where the parameter values are ordered, alpha_1 <= ... <= alpha_K, then any permutation will yield a new ordering of the parameters, alpha_{sigma(1)} <= ... <= alpha_{sigma(K)}, which then identifies another labeling. In other words, we can identify each labeling by the ordering of the parameter values.

This identification also has a welcome geometric interpretation. The region of parameter space satisfying a given ordering constraint, such as alpha_1 <= ... <= alpha_K, defines a square pyramid with the apex point at zero. The K-dimensional parameter space neatly decomposes into K! of these pyramids, each with a distinct ordering and hence association with a unique labeling.

When the priors are exchangeable the mixture posterior _aliases_ across each of these pyramids in parameter space: if we were given the mixture posterior restricted to one of these pyramids then we could reconstruct the entire mixture distribution by simply rotating that restricted distribution into each of the other K! - 1 pyramids. As we do this we also map the mode in the restricted distribution into each pyramid, creating exactly the expected K! multimodality.

#### Exchangeable Inferences and Ordering Constraints

From a Bayesian perspective, all well-defined inferences are given by expectations of certain functions with respect to our posterior distribution. Hence if we want to limit ourselves to only those inferences insensitive to the labeling then we have to consider expectations only of those functions that are permutation invariant, f(sigma(alpha)) = f(alpha).

Importantly, under this class of functions the symmetry of the degenerate mixture posterior carries over to the expectation values themselves: the expectation taken over each pyramid will yield exactly the same value. Consequently we should be able to avoid the combinatorial cost of fitting the full mixture model by simply restricting our exploration to a single ordering of the parameters.

Imposing an ordering on parameter space can be taken as a computational trick, but it can also be interpreted as method of making an exchangeable prior non-exchangeable without affecting the resulting inferences. Given the exchangeable prior pi(alpha) we define the non-exchangeable prior

    pi'(alpha) = { pi(alpha),  if alpha_1 <= ... <= alpha_K
                 { 0,          else

which limits the mixture posterior, and hence any expectations, to a single ordering. From this perspective _all_ of our strategies for breaking the labeling degeneracy reduce to imposing a non-exchangeable prior.

While the ordering is limited to scalar parameters, it can still prove useful when the component distributions are multivariate. Although we cannot order the multivariate parameters themselves, ordering any one of the parameters is sufficient to break the labeling degeneracy for the entire mixture.

## A Bayesian Mixture Model Example

To illustrate the pathologies of Bayesian mixture models, and their potential resolutions, let's consider a relatively simple example where the likelihood is given by a mixture of two Gaussians,

    pi(y_1, ..., y_N | mu_1, sigma_1, mu_2, sigma_2, theta_1, theta_2) = sum_{n=1}^{N} theta_1 * N(y_n | mu_1, sigma_1) + theta_2 * N(y_n | mu_2, sigma_2).

Note that the mixture is applied to each datum individually -- our model assumes that each measurement is drawn from one of the components independently as opposed to the entire dataset being drawn from one of the components as a whole.

We first define the component data generating processes to be well-separated relative to their standard deviations,

```r
mu <- c(-2.75, 2.75);
sigma <- c(1, 1);
lambda <- 0.4
```

Then we simulate some data from the mixture likelihood by following its generative structure, first drawing assignments for each measurement and then drawing the measurements themselves from the corresponding Gaussian,

```r
set.seed(689934)

N <- 1000
z <- rbinom(N, 1, lambda) + 1;
y <- rnorm(N, mu[z], sigma[z]);

library(rstan)
rstan_options(auto_write = TRUE)

stan_rdump(c("N", "y"), file="mix.data.R")
```

### A Degenerate Implementation

As discussed above, in order to ensure that the labeling degeneracies persist in the posterior distribution we need exchangeable priors. We can, for example, accomplish this by assigning the identical priors to the Gaussian parameters,

    mu_1, mu_2 ~ N(0, 2), sigma_1, sigma_2 ~ Half-N(0, 2),

and a symmetric Beta distribution to the mixture weight,

    theta_1 ~ Beta(5, 5).

```stan
data {
 int<lower = 0> N;
 vector[N] y;
}

parameters {
  vector[2] mu;
  real<lower=0> sigma[2];
  real<lower=0, upper=1> theta;
}

model {
 sigma ~ normal(0, 2);
 mu ~ normal(0, 2);
 theta ~ beta(5, 5);
 for (n in 1:N)
   target += log_mix(theta,
                     normal_lpdf(y[n] | mu[1], sigma[1]),
                     normal_lpdf(y[n] | mu[2], sigma[2]));
}
```

Equivalently we could also have defined theta as a two-dimensional simplex with a Dirichlet(5, 5) prior which would yield the same exact model.

Aware of the labeling degeneracy, let's go ahead and fit this Bayesian mixture model in Stan,

```r
input_data <- read_rdump("mix.data.R")

degenerate_fit <- stan(file='gauss_mix.stan', data=input_data,
                       chains=4, seed=483892929, refresh=2000)
```

The split Rhat is atrocious, indicating that the chains are not exploring the same regions of parameter space:

```
              mean se_mean   sd     2.5%      25%      50%      75%    97.5% n_eff  Rhat
mu[1]       -1.33    1.72 2.43    -2.81    -2.75    -2.72    -1.26     2.94     2 56.48
mu[2]        1.47    1.72 2.43    -2.79     1.36     2.85     2.89     2.96     2 51.11
sigma[1]     1.03    0.00 0.03     0.96     1.00     1.03     1.05     1.09  4000  1.00
sigma[2]     1.02    0.00 0.04     0.95     1.00     1.02     1.05     1.10  4000  1.00
theta        0.56    0.07 0.11     0.36     0.53     0.62     0.63     0.65     2  7.52
lp__     -2108.57    0.03 1.55 -2112.46 -2109.43 -2108.28 -2107.43 -2106.51  2050  1.00
```

Indeed this is to be expected as the individual chains find and then explore one of the two degenerate modes independently of the others.

### An Identified Implementation (Ordering Constraint)

The identified model uses `ordered[2] mu` to enforce mu_1 <= mu_2, breaking the labeling degeneracy:

```stan
data {
 int<lower = 0> N;
 vector[N] y;
}

parameters {
  ordered[2] mu;
  real<lower=0> sigma[2];
  real<lower=0, upper=1> theta;
}

model {
 sigma ~ normal(0, 2);
 mu ~ normal(0, 2);
 theta ~ beta(5, 5);
 for (n in 1:N)
   target += log_mix(theta,
                     normal_lpdf(y[n] | mu[1], sigma[1]),
                     normal_lpdf(y[n] | mu[2], sigma[2]));
}
```

The critical identifying feature is `ordered[2] mu`, which enforces the constraint that mu_1 <= mu_2. This breaks the labeling degeneracy inherent to mixture models by restricting the posterior to a single ordering region of parameter space. With this constraint, all chains explore the same mode, R-hat values converge to 1.0, and the model produces reliable inferences.

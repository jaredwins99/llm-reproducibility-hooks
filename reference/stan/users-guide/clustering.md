# Clustering Models

## Overview

This Stan documentation page covers unsupervised clustering methods. The chapter describes implementation of statistical clustering models including soft K-means, latent Dirichlet allocation (LDA), and naive Bayesian classification.

## Relation to Finite Mixture Models

Clustering models and finite mixture models are fundamentally related. The "soft" K-means model represents a normal mixture model, while latent Dirichlet allocation functions as a mixed-membership multinomial mixture.

## Soft K-means

K-means clustering organizes D-dimensional vectors into K clusters. The approach treats cluster assignments probabilistically rather than deterministically.

### Geometric Hard K-means Algorithm

The traditional algorithm follows these steps:

1. Randomly assign each vector yn to a cluster in {1,...,K}
2. Repeat until convergence:
   - Compute cluster centroids μk by averaging assigned vectors
   - Reassign each yn to the nearest cluster (by Euclidean distance)
   - Stop if no vectors changed clusters

### Soft K-means Clustering

Soft K-means extends this by treating assignments as probability distributions. The connection between Euclidean distance and multivariate normal distributions with fixed covariance enables implementation as a mixture model.

**Generative Model:**
- Cluster assignment: "zn ~ categorical(1/K)"
- Data generation: "yn ~ normal(μz[n], Σz[n])"

The implementation assumes unit covariance: "Σk = diag_matrix(1)"

The log probability becomes proportional to: "exp(−1/2 Σd(μk,d − yn,d)^2)"

### Stan Implementation Example

```stan
data {
  int<lower=0> N;        // number of data points
  int<lower=1> D;        // number of dimensions
  int<lower=1> K;        // number of clusters
  array[N] vector[D] y;  // observations
}
transformed data {
  real<upper=0> neg_log_K;
  neg_log_K = -log(K);
}
parameters {
  array[K] vector[D] mu; // cluster means
}
transformed parameters {
  array[N, K] real<upper=0> soft_z; // log unnormalized clusters
  for (n in 1:N) {
    for (k in 1:K) {
      soft_z[n, k] = neg_log_K
                     - 0.5 * dot_self(mu[k] - y[n]);
    }
  }
}
model {
  // prior
  for (k in 1:K) {
    mu[k] ~ std_normal();
  }

  // likelihood
  for (n in 1:N) {
    target += log_sum_exp(soft_z[n]);
  }
}
```

The transformed parameters contain log unnormalized cluster assignment probabilities, convertible to normalized simplex using softmax.

### Generalizations

Replacing the normal distribution with double exponential creates L1-distance clustering. Per-cluster covariance matrices accommodate different geometries, though spatial analogs don't exist. Hierarchical priors can regularize covariance estimation.

## Bayesian Inference Challenges

Two fundamental issues complicate clustering inference:

### Non-identifiability

Cluster label permutations produce identical likelihoods. The parameter vector μ lacks identifiability -- swapping indices yields equivalent models. This prevents meaningful parameter comparison across chains and even within single chains with sufficient length.

### Multimodality

Clustering posteriors exhibit extreme multimodality beyond label-switching effects. This prevents proper posterior exploration and accurate integral evaluation for posterior predictive inference.

**Practical Guidance:** Fit multiple initializations and select the sample with highest probability. Consider optimization-based approaches like expectation maximization or variational Bayes instead of sampling.

## Naive Bayes Classification and Clustering

Naive Bayes implements multinomial mixture models applicable to classification, clustering, or semi-supervised learning depending on observed labels.

### Model Structure

**Data:** M documents with Nm words each from vocabulary V

**Categories:** K topics or categories

**Generative Process:**
- Document category: "zm ~ categorical(θ)"
- Words (conditional independence): "wm,n ~ categorical(φz[m])"

Parameters θ (category prevalence) and φ (word distributions) typically receive symmetric Dirichlet priors.

### Coding Ragged Arrays

Since Stan lacks ragged array support, the implementation uses a global word list with document indices:

| Index n | Word w[n] | Document doc[n] |
|---------|-----------|-----------------|
| 1       | w1,1      | 1               |
| 2       | w1,2      | 1               |
| ...     | ...       | ...             |

### Supervised Implementation (Category-Labeled Data)

```stan
data {
  int<lower=1> K;               // num topics
  int<lower=1> V;               // num words
  int<lower=0> M;               // num docs
  int<lower=0> N;               // total word instances
  array[M] int<lower=1, upper=K> z;    // topic for doc m
  array[N] int<lower=1, upper=V> w;    // word n
  array[N] int<lower=1, upper=M> doc;  // doc ID for word n
  vector<lower=0>[K] alpha;     // topic prior
  vector<lower=0>[V] beta;      // word prior
}
parameters {
  simplex[K] theta;             // topic prevalence
  array[K] simplex[V] phi;      // word dist for topic k
}
model {
  theta ~ dirichlet(alpha);
  for (k in 1:K) {
    phi[k] ~ dirichlet(beta);
  }
  for (m in 1:M) {
    z[m] ~ categorical(theta);
  }
  for (n in 1:N) {
    w[n] ~ categorical(phi[z[doc[n]]]);
  }
}
```

### Unsupervised Implementation (Clustering)

Without category labels, the discrete assignment variable z requires marginalization:

**Marginal document probability:**

p(wm,1,...,wm,Nm | θ,φ) = log Σk [categorical(k | θ) * Πn categorical(wm,n | φk)]

Converting to log scale for numerical stability:

```
= log Σk exp(log categorical(k | θ) + Σn log categorical(wm,n | φk))
```

**Stan Implementation:**

```stan
model {
  array[M, K] real gamma;
  theta ~ dirichlet(alpha);
  for (k in 1:K) {
    phi[k] ~ dirichlet(beta);
  }
  for (m in 1:M) {
    for (k in 1:K) {
      gamma[m, k] = categorical_lpmf(k | theta);
    }
  }
  for (n in 1:N) {
    for (k in 1:K) {
      gamma[doc[n], k] = gamma[doc[n], k]
                         + categorical_lpmf(w[n] | phi[k]);
    }
  }
  for (m in 1:M) {
    target += log_sum_exp(gamma[m]);
  }
}
```

The variable γm,k represents: "log categorical(k | θ) + Σn log categorical(wm,n | φk)"

**Posterior category probability:** Pr[zm = k | w, α, β] = exp(γm,k - log Σk' exp(γm,k'))

### Full Bayesian Inference

Combine labeled and unlabeled data models. Unlabeled data contributes to parameter estimation without providing category information, implementing semi-supervised learning with missing category labels.

### Prediction Without Updates

Move γ definition to the generated quantities block to prevent unlabeled data from influencing parameter estimates.

## Latent Dirichlet Allocation

LDA generalizes naive Bayes through mixed-membership modeling where each document contains multiple topics.

### The LDA Model

**Per-document topic distribution:** "θm ~ Dirichlet(α)" (hyperparameter α is K-vector)

**Topic assignment for word n:** "zm,n ~ categorical(θm)"

**Word generation:** "wm,n ~ categorical(φz[m,n])"

**Topic word distributions:** "φk ~ Dirichlet(β)" (hyperparameter β is V-vector)

### Marginalizing Discrete Parameters

The joint posterior marginalizes topic and word assignments:

p(θ,φ | w,α,β) ∝ p(θ | α) p(φ | β) p(w | θ,φ)

Inner word probability (summing over topic assignments):

p(wm,n | θm,φ) = Σz p(z | θm) p(wm,n | φz)

**Log-scale formula:**

log p(θ,φ | w,α,β) = Σm log Dirichlet(θm | α) + Σk log Dirichlet(φk | β)
                     + Σm Σn log(Σz categorical(z | θm) * categorical(wm,n | φz))

### Stan Implementation

```stan
data {
  int<lower=2> K;               // num topics
  int<lower=2> V;               // num words
  int<lower=1> M;               // num docs
  int<lower=1> N;               // total word instances
  array[N] int<lower=1, upper=V> w;    // word n
  array[N] int<lower=1, upper=M> doc;  // doc ID for word n
  vector<lower=0>[K] alpha;     // topic prior
  vector<lower=0>[V] beta;      // word prior
}
parameters {
  array[M] simplex[K] theta;    // topic dist for doc m
  array[K] simplex[V] phi;      // word dist for topic k
}
model {
  for (m in 1:M) {
    theta[m] ~ dirichlet(alpha);  // prior
  }
  for (k in 1:K) {
    phi[k] ~ dirichlet(beta);     // prior
  }
  for (n in 1:N) {
    array[K] real gamma;
    for (k in 1:K) {
      gamma[k] = log(theta[doc[n], k]) + log(phi[k, w[n]]);
    }
    target += log_sum_exp(gamma);  // likelihood;
  }
}
```

### Correlated Topic Model

Blei and Lafferty (2007) replaced the Dirichlet prior on topic distributions with a multivariate logistic normal distribution to account for topic correlations.

#### Fixed Hyperparameter Variant

Replace Dirichlet prior with multivariate logistic normal:

```stan
data {
  // ... data as before without alpha ...
  vector[K] mu;          // topic mean
  cov_matrix[K] Sigma;   // topic covariance
}
parameters {
  array[K] simplex[V] phi;     // word dist for topic k
  array[M] vector[K] eta;      // topic dist for doc m
}
transformed parameters {
  array[M] simplex[K] theta;
  for (m in 1:M) {
    theta[m] = softmax(eta[m]);
  }
}
model {
  for (m in 1:M) {
    eta[m] ~ multi_normal(mu, Sigma);
  }
  // ... model as before w/o prior for theta ...
}
```

#### Full Bayes Variant

Move μ and Σ to parameters with priors:

```stan
parameters {
  vector[K] mu;              // topic mean
  corr_matrix[K] Omega;      // correlation matrix
  vector<lower=0>[K] sigma;  // scales
  array[M] vector[K] eta;    // logit topic dist for doc m
  array[K] simplex[V] phi;   // word dist for topic k
}
transformed parameters {
  cov_matrix[K] Sigma;       // covariance matrix
  for (m in 1:K) {
    Sigma[m, m] = sigma[m] * sigma[m] * Omega[m, m];
  }
  for (m in 1:(K-1)) {
    for (n in (m+1):K) {
      Sigma[m, n] = sigma[m] * sigma[n] * Omega[m, n];
      Sigma[n, m] = Sigma[m, n];
    }
  }
}
model {
  mu ~ normal(0, 5);      // vectorized, diffuse
  Omega ~ lkj_corr(2.0);  // regularize to unit correlation
  sigma ~ cauchy(0, 5);   // half-Cauchy due to constraint
  // ... words sampled as above ...
}
```

The LKJCorr distribution with shape α > 0 supports correlation matrices. Formula: "LkjCorr(Ω|α) ∝ det(Ω)^(α-1)". With α = 2, this weakly favors unit correlations, indirectly regularizing covariance toward diagonal structures.

## References

Blei, David M., and John D. Lafferty. 2007. "A Correlated Topic Model of *Science*." *The Annals of Applied Statistics* 1 (1): 17-37.

Blei, David M., Andrew Y. Ng, and Michael I. Jordan. 2003. "Latent Dirichlet Allocation." *Journal of Machine Learning Research* 3: 993-1022.

Gelman, Andrew, et al. 2013. *Bayesian Data Analysis*. Third Edition. Chapman & Hall / CRC Press.

Gelman, Andrew, and Jennifer Hill. 2007. *Data Analysis Using Regression and Multilevel-Hierarchical Models*. Cambridge University Press.

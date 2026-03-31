# Typical Sets and the Curse of Dimensionality

**Bob Carpenter** | 11 April 2017

Source: https://mc-stan.org/learn-stan/case-studies/curse-dims.html

---

## Abstract

This case study illustrates the curse of dimensionality through simulation. Key observations include:

- Generating random points uniformly in a unit hypercube shows that the average distance between random points increases with dimensionality
- Such points increasingly fall outside the hypersphere inscribed within the hypercube, revealing that higher dimensions concentrate most volume in corners
- Standard normal variates concentrate in a thin shell at increasing distance from the mean as dimensions grow
- The squared distance from the mode follows a chi-square distribution, allowing precise calculation of thin shell bounds
- The typical set for a normal distribution in high dimensions does NOT include the volume around the mode, since probability mass equals density multiplied by volume
- Standard normal log density equals negative squared Euclidean distance, demonstrating why maximum likelihood estimates for normal regression match least squares solutions

## 1. Euclidean Length and Distance

### Euclidean Length

The Euclidean length of a vector y = (y_1, ..., y_n) is defined as:

    ||y|| = sqrt(y_1^2 + y_2^2 + ... + y_n^2)

In R, this can be computed as:

```r
euclidean_length <- function(u) sqrt(sum(u * u));
```

Testing with the classic 3-4-5 triangle:

```r
euclidean_length(c(3, 4));
# [1] 5
```

Note: R's `length()` function returns the number of elements, not Euclidean length.

### Euclidean Distance

The Euclidean distance between N-vectors x and y is:

    d(x, y) = ||x - y|| = sqrt((x_1 - y_1)^2 + ... + (x_n - y_n)^2)

## 2. All of the Volume is in the Corners

Consider an N-dimensional hypercube with unit-length sides centered at the origin, with corners at (+/-1/2, ..., +/-1/2). The hypercube has volume 1 since 1^N = 1.

The largest inscribed hypersphere has radius 1/2. A point y lies within this hypersphere if ||y|| < 1/2.

Key observation: As dimensionality increases, most points in the hypercube lie outside the inscribed hypersphere. This demonstrates that in higher dimensions, almost all of the volume is in the corners of the hypercube.

### Simulation

```r
# Fraction of uniform hypercube samples falling inside inscribed hypersphere
fraction_inside <- function(N, M = 1e5) {
  count <- 0
  for (m in 1:M) {
    y <- runif(N, -0.5, 0.5)
    if (euclidean_length(y) < 0.5)
      count <- count + 1
  }
  count / M
}
```

Results show the fraction inside drops rapidly:
- N=1: ~1.0
- N=2: ~0.785 (pi/4)
- N=5: ~0.164
- N=10: ~0.003
- N=20: ~0.0

### Volume Formula

The volume of an N-dimensional hypersphere of radius r is:

    V_N(r) = (pi^(N/2) / Gamma(N/2 + 1)) * r^N

The ratio of hypersphere to hypercube volume (with hypercube side = 2r) is:

    V_N(r) / (2r)^N = pi^(N/2) / (2^N * Gamma(N/2 + 1))

This ratio goes to 0 as N grows, confirming that the corners dominate.

## 3. Distance Between Random Points

As dimensionality increases, the distance between pairs of uniformly sampled points concentrates around a specific value with decreasing relative variance. In high dimensions, all points appear roughly equidistant from each other.

```r
# Pairwise distances in N dimensions
pairwise_distances <- function(N, M = 1000) {
  dists <- c()
  for (i in 1:(M-1)) {
    x <- runif(N, -0.5, 0.5)
    for (j in (i+1):M) {
      y <- runif(N, -0.5, 0.5)
      dists <- c(dists, euclidean_length(x - y))
    }
  }
  dists
}
```

## 4. Standard Normal Distributions in High Dimensions

### Concentration in a Thin Shell

For a standard normal distribution in N dimensions, the squared distance from the origin follows a chi-squared distribution with N degrees of freedom:

    sum_{n=1}^{N} y_n^2 ~ chi^2(N)

The chi-squared distribution has:
- Mean = N
- Variance = 2N

Therefore the distance from the origin concentrates around sqrt(N) with standard deviation sqrt(2N) / (2*sqrt(N)) = sqrt(1/2).

As N grows, essentially all probability mass lies in a thin shell at distance approximately sqrt(N) from the origin.

### The Mode is Not in the Typical Set

This creates a paradox: the mode of the N-dimensional standard normal is at the origin (where density is highest), but essentially no probability mass exists near the origin in high dimensions. The probability of any region depends on the product of density and volume. Near the origin, density is high but volume is vanishingly small. At distance sqrt(N), density is lower but the shell volume is enormous.

The **typical set** is the region where most probability mass concentrates -- the thin shell at distance ~sqrt(N), NOT the region around the mode.

## 5. Connection to Regression and Least Squares

The standard normal log density for a vector y = (y_1, ..., y_N) is:

    log p(y) = -N/2 * log(2*pi) - 1/2 * sum_{n=1}^{N} y_n^2
             = -N/2 * log(2*pi) - 1/2 * ||y||^2

Since the log density is a linear function of the negative squared Euclidean distance, maximizing the normal log-likelihood is equivalent to minimizing the sum of squared errors. This demonstrates why maximum likelihood estimation in normal regression produces identical results to ordinary least squares optimization.

## Practical Implications for MCMC

Understanding the typical set is crucial for MCMC:

1. **Initialization**: Starting chains at the mode (MAP estimate) places them outside the typical set in high dimensions. The sampler must first find the typical set before producing useful samples.

2. **Sampling efficiency**: Algorithms that can efficiently explore the thin shell structure of the typical set (like HMC) dramatically outperform random-walk methods that waste time in low-probability regions.

3. **Convergence assessment**: Chains should be assessed for convergence to the typical set, not convergence to the mode.

4. **Prior predictive checks**: Understanding how probability mass concentrates helps calibrate prior distributions in high-dimensional models.

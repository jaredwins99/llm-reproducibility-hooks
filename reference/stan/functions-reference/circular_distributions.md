# Circular Distributions

Circular distributions apply to finite values within any interval spanning 2*pi.

## Von Mises Distribution

### Probability Density Function

For mu in R and kappa in R+, the density is:

VonMises(y|mu,kappa) = exp(kappa*cos(y-mu)) / (2*pi*I_0(kappa))

The variable y must be restricted to an interval (c, c + 2*pi) of length 2*pi for proper normalization.

When kappa > 0, the distribution exhibits a single mode at mu when the 2*pi support interval centers around the location parameter. If mu is not centered within the support, a second local maximum appears at the boundary furthest from the mode.

When kappa = 0, the distribution becomes circular uniform with density 1/(2*pi), independent of y or mu values.

### Distribution Statement

```
y ~ von_mises(mu, kappa)
```

Increments target log probability with `von_mises_lupdf(y | mu, kappa)`.

*Available since 2.0*

### Stan Functions

**`real von_mises_lpdf(reals y | reals mu, reals kappa)`**
Log probability density function. *Available since 2.18*

**`real von_mises_lupdf(reals y | reals mu, reals kappa)`**
Log probability density dropping constant terms. *Available since 2.25*

**`real von_mises_cdf(reals y | reals mu, reals kappa)`**
Cumulative distribution function. *Available since 2.29*

**`real von_mises_lcdf(reals y | reals mu, reals kappa)`**
Log cumulative distribution function. *Available since 2.29*

**`real von_mises_lccdf(reals y | reals mu, reals kappa)`**
Log complementary cumulative distribution function. *Available since 2.29*

**`R von_mises_rng(reals mu, reals kappa)`**
Generates variates in the interval [(mu mod 2*pi)-pi, (mu mod 2*pi)+pi]. For generation only in transformed data and generated quantities blocks. *Available since 2.18*

### Numerical Stability

For kappa > 100, the implementation becomes numerically unstable. As kappa -> inf, the Von Mises approaches Normal(mu, sqrt(1/kappa)).

**Recommended workaround:**

```stan
if (kappa < 100) {
  y ~ von_mises(mu, kappa);
} else {
  y ~ normal(mu, sqrt(1 / kappa));
}
```

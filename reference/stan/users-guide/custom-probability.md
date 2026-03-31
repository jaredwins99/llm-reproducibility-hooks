# Custom Probability Functions

## Overview

Stan enables direct implementation of custom probability distributions within its programming language. The core mechanism involves incrementing the total log probability, allowing users to define distributions not included in Stan's built-in library.

## Examples

### Triangle Distribution

The symmetric triangle distribution features a density shaped like an isosceles triangle bounded by parameters α and β (where α < β). For y ∈ (α,β), the density is:

```
triangle(y | α,β) = 1/(β - α)² · min(y - α, β - y)
```

**General Implementation:**

```stan
data {
  real alpha;
  real<lower=alpha> beta;
}
parameters {
  real<lower=alpha, upper=beta> y;
}
model {
  target += -2 * log(beta - alpha)
    + log(fmin(y - alpha, beta - y));
}
```

When bounds are fixed data, the constant term `-2 * log(beta - alpha)` can be dropped for efficiency.

**Simplified Case (α = -1, β = 1):**

```stan
parameters {
  real<lower=-1, upper=1> y;
}
model {
  target += log1m(abs(y));
}
```

Here, `log1m(abs(y))` computes log(1 - |y|) with superior numerical stability compared to direct calculation.

**Critical Note:** Declaring `y` with explicit bounds (`real<lower=-1, upper=1>`) is essential for correct sampling. Without this constraint, the sampler may explore invalid regions and produce arithmetic errors. The constrained declaration ensures an automatic inverse logit transform is applied.

### Exponential Distribution

A basic exponential distribution implementation without Stan's built-in function:

```stan
target += log(lambda) - y * lambda;
```

This works identically to the distribution statement `y ~ exponential(lambda);` except the built-in version performs input validation and automatically drops constant terms when λ is not a parameter.

### Bivariate Normal CDF

The following implements the bivariate normal cumulative distribution function with zero location, unit variance, and correlation ρ:

```stan
real binormal_cdf(tuple(real, real) z, real rho) {
  real z1 = z.1;
  real z2 = z.2;
  if (z1 == 0 && z2 == 0) {
    return 0.25 + asin(rho) / (2 * pi());
  }
  real denom = sqrt((1 + rho) * (1 - rho));
  real term1 = z1 == 0
    ? (z2 > 0 ? 0.25 : -0.25)
    :  owens_t(z1, (z2 / z1 - rho) / denom);
  real term2 = z2 == 0
    ? (z1 > 0 ? 0.25 : -0.25)
    : owens_t(z2, (z1 / z2 - rho) / denom);
  real z1z2 = z1 * z2;
  real delta = z1z2 < 0 || (z1z2 == 0 && (z1 + z2) < 0);
  return 0.5 * (Phi(z1) + Phi(z2) - delta) - term1 - term2;
}
```

The tuple argument enables calling syntax: `binormal_cdf((z1, z2) | rho)`.

**Testing approach:**

```stan
transformed data {
  for (zzr in {[0, 0, 0.5],
               [0, 1, 0.5],
               [1, 0, -0.2],
               [1, 3, 0.9]}) {
    real z1  = zzr[1];
    real z2 = zzr[2];
    real rho = zzr[3];
    print("binomial_cdf((",  z1, ", ", z2, ") | ", rho, ")",
          "=", binormal_cdf((z1, z2) | rho));
  }
}
```

Results can be validated against existing packages like R's `pbivnorm`.

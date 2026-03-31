# Computing One Dimensional Integrals

## Overview

Stan enables computation of definite and indefinite one-dimensional integrals using the `integrate_1d` function. This capability proves essential for normalizing probability distributions where truncation points or other integral-dependent parameters need estimation.

## Defining the Integrand

The integrand must be implemented as a Stan function with a specific signature. For example, computing the normalizing constant of a left-truncated normal distribution:

```stan
real normal_density(real x,             // Function argument
                    real xc,            // Complement of function argument
                                        //  on the domain (defined later)
                    array[] real theta, // parameters
                    array[] real x_r,   // data (real)
                    array[] int x_i) {  // data (integer)
  real mu = theta[1];
  real sigma = theta[2];

  return 1 / (sqrt(2 * pi()) * sigma) * exp(-0.5 * ((x - mu) / sigma)^2);
}
```

**Key parameters:**
- `x`: The integration variable
- `xc`: High-precision distance to nearest integration limit (definite integrals only; NaN for infinite limits)
- `theta`: Model parameters as a function of data/transformed data/parameters
- `x_r`, `x_i`: Real and integer data (must be included even if unused)

## Calling the Integrator

### Example Model

```stan
data {
  int N;
  array[N] real y;
}

transformed data {
  array[0] real x_r;
  array[0] int x_i;
}

parameters {
  real mu;
  real<lower=0.0> sigma;
  real left_limit;
}

model {
  mu ~ normal(0, 1);
  sigma ~ normal(0, 1);
  left_limit ~ normal(0, 1);
  target += normal_lpdf(y | mu, sigma);
  target += -log(integrate_1d(normal_density,
                              left_limit,
                              positive_infinity(),
                              { mu, sigma }, x_r, x_i));
}
```

### Limits of Integration

Integration bounds can be finite or infinite using `negative_infinity()` and `positive_infinity()`. When both limits are infinite, the integral and gradients return zero.

### Data vs. Parameters

Data arguments (`x_r`, `x_i`) must involve only data or transformed data. The `theta` vector can depend on parameters and transformed parameters. Integration endpoints themselves can be data or parameters, with derivatives handled via the Leibniz integral rule.

## Convergence Behavior

The integrator employs iterative double exponential quadrature from the Boost library. Iteration terminates when:

$$\frac{|I_{n+1} - I_n|}{|I_{n+1}|} < \text{relative tolerance}$$

The default relative tolerance equals the square root of machine epsilon for double precision (~1e-8). Exceptions arise when convergence cannot be achieved; specifying a larger `relative_tolerance` parameter may resolve this.

### Zero-Crossing Integrals

Integrals crossing zero split into two parts: one from (a, 0) and another from (0, b). Each integrates separately to the specified tolerance, since quadrature methods struggle near zero.

## Precision at Integration Limits

Numerical breakdown occurs near definite integral endpoints due to floating-point precision limits. The `xc` parameter provides remedy by offering high-precision distance calculations.

### Beta Distribution Example

The unnormalized beta PDF is proportional to:
$$x^{\alpha - 1}(1 - x)^{\beta - 1}$$

Naive implementation fails for small alpha and beta because computing (1 - x) loses precision as x approaches one:

```stan
real beta(real x, real xc, array[] real theta, array[] real x_r, array[] int x_i) {
  real alpha = theta[1];
  real beta = theta[2];
  real v;

  if(x > 0.5) {
    v = x^(alpha - 1.0) * xc^(beta - 1.0);
  } else {
    v = x^(alpha - 1.0) * (1.0 - x)^(beta - 1.0);
  }

  return v;
}
```

Near the upper limit (x approaching 1), `xc` provides the value of (1 - x) with high precision.

### Shifted Log-Normal Example

For a shifted log-normal distribution truncated at b, computing the expectation requires:

$$\int_{\delta}^b xf(x)\,dx$$

The PDF helper function:

```stan
real shift_lognormal_pdf(real x,
                         real mu,
                         real sigma,
                         real delta) {
  real p;

  p = (1.0 / ((x - delta) * sigma * sqrt(2 * pi()))) *
    exp(-1 * (log(x - delta) - mu)^2 / (2 * sigma^2));

  return p;
}
```

When integrating from delta, the term (x - delta) becomes very small, causing numerical issues. The refined integrand uses `xc`:

```stan
real integrand(real x,
               real xc,
               array[] real theta,
               array[] real x_r,
               array[] int x_i) {
  real numerator;
  real p;

  real mu = theta[1];
  real sigma = theta[2];
  real delta = theta[3];
  real b = theta[4];

  if (x < delta + 1) {
    p = shift_lognormal_pdf(xc, mu, sigma, delta);
  } else {
    p = shift_lognormal_pdf(x, mu, sigma, delta);
  }

  numerator = x * p;

  return numerator;
}
```

When x lies near delta (the lower bound), `xc` effectively equals x with higher precision, avoiding the (x - delta) precision loss.

**Note:** `xc` applies only to definite integrals. For zero-crossing definite integrals, `xc` represents high-precision distances to the respective limits of the two sub-integrals.

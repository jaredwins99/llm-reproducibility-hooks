# Conventions for Probability Functions

## Suffix Marks Type of Function

Stan uses standardized suffixes to indicate function types:

| Function | Outcome | Suffix |
|----------|---------|--------|
| Log probability mass function | Discrete | `_lpmf` |
| Log probability density function | Continuous | `_lpdf` |
| Log cumulative distribution function | Any | `_lcdf` |
| Log complementary cumulative distribution function | Any | `_lccdf` |
| Random number generator | Any | `_rng` |

Examples include `normal_lpdf` for the normal density and `bernoulli_lpmf` for the Bernoulli mass function.

## Argument Order and the Vertical Bar

Probability functions use a vertical bar separating outcome values from distribution parameters. The syntax is `function_name(outcome | parameters)`. For instance, `normal_lpdf(y | mu, sigma)` returns the log-density value.

## Sampling Notation

Two equivalent forms exist:

```stan
y ~ normal(mu, sigma);
```

produces the same proportional contribution as:

```stan
target += normal_lpdf(y | mu, sigma);
```

The sampling notation drops additive constants unnecessary for sampling and optimization.

## Finite Inputs

All distribution functions throw exceptions when supplied non-finite arguments (infinite values or NaN).

## Boundary Conditions

Distributions with constrained parameter support throw exceptions when constraints are violated. For example, `normal_lpdf` rejects `sigma = 0` since the scale parameter requires sigma > 0.

## Pseudorandom Number Generators

PRNG functions use the `_rng` suffix, like `normal_rng(real, real)`.

### Restrictions

PRNG functions are restricted to transformed data and generated quantities blocks only.

### Limited Vectorization

Only some PRNG functions support vectorization, unlike probability functions.

## Cumulative Distribution Functions

For univariate random variable Y with probability function p_Y(y|theta):

**CDF**: F_Y(y) = Pr[Y <= y] = integral_{-inf}^y p(y|theta) dy

**CCDF**: Pr[Y > y] = 1 - F_Y(y)

Log forms are available for most univariate distributions. The CCDF is numerically preferred because representable values near 0 (approx 10^{-300}) exist, but near 1 only to approx 1 - 10^{-15}.

## Vectorization

Vectorized functions sum over elementwise applications.

### Vectorized Function Signatures

The pseudotype `reals` indicates arguments accepting real scalars, one-dimensional arrays, vectors, or row-vectors. When multiple array/vector arguments exist, sizes must match.

Example: `normal_lpdf(reals | reals, reals)`

Multivariate distributions use: `multi_normal_lpdf(vectors | vectors, matrix)`

The pseudotype `ints` represents vectorized integer arguments.

### Evaluating Vectorized Log Probability Functions

Results equal the sum of elementwise evaluations. Non-vector arguments repeat across elements.

If `y` and `mu` are size-N vectors and `sigma` is scalar:

```stan
ll = normal_lpdf(y | mu, sigma);
```

equals:

```stan
ll = 0;
for (n in 1:N) {
  ll = ll + normal_lpdf(y[n] | mu[n], sigma);
}
```

Similarly, `y ~ normal(mu, sigma)` matches the effect of looping element-wise assignments.

### Evaluating Vectorized PRNG Functions

Some PRNG functions accept sequences. Output is also a sequence. Example:

```stan
vector[3] mu = // ...
array[3] real x = normal_rng(mu, 3);
```

#### Argument Types for PRNG

| Pseudotype | Allowable Arguments |
|------------|-------------------|
| `ints` | `int`, `array[] int` |
| `reals` | `int`, `array[] int`, `real`, `array[] real`, `vector`, `row_vector` |

#### Dimension Matching

Multiple non-scalar PRNG arguments must share dimensions but need not share types:

```stan
vector[3] mu = // ...
array[3] real sigma = // ...
array[3] real x = normal_rng(mu, sigma);
```

#### Return Type

If all arguments are scalar, returns a scalar. For continuous distributions with non-scalar arguments, returns `array[] real` matching size. Discrete distributions return `ints` and continuous return `reals` of appropriate dimensions.

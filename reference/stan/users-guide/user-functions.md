# User-Defined Functions in Stan

## Overview

User-defined functions allow computations to be encapsulated into named units and reused throughout a Stan program. As the documentation notes, "Writing modular code using descriptively named functions is easier to understand than a monolithic program."

## Basic Function Structure

Functions are defined in a dedicated `functions` block that must appear before all other program blocks. A simple example demonstrates the pattern:

```stan
functions {
  real relative_diff(real x, real y) {
    real abs_diff;
    real avg_scale;
    abs_diff = abs(x - y);
    avg_scale = (abs(x) + abs(y)) / 2;
    return abs_diff / avg_scale;
  }
}
```

### Key Components

**Return Statements**: Return statements are only permitted within function definitions and may appear anywhere in the function body. Non-void functions must end with a return statement.

**Function Bodies**: The body contains ordinary Stan code, including local variable declarations. Functions access the same built-in operations available elsewhere in Stan programs.

**Type Declarations**: Function arguments and return types for vectors and matrices are declared without size specifications. Constraints (bounds or structured constraints) are not permitted in function declarations, even though the variables may satisfy such constraints at runtime.

### Error Handling

Stan provides two mechanisms for reporting errors:

The `reject` statement flags errors and accepts quoted strings or expressions as arguments. It's commonly used to validate inputs:

```stan
real dbl_sqrt(real x) {
  if (!(x >= 0)) {
    reject("dbl_sqrt(x): x must be positive; found x = ", x);
  }
  return 2 * sqrt(x);
}
```

The `fatal_error` statement addresses unrecoverable errors. Rejection behavior depends on context: in transformed data blocks it prevents program loading; in transformed parameters or model blocks it causes state rejection in the Metropolis sense; in generated quantities it produces NaN values.

## Specialized Function Types

### Void Functions

Functions with `void` return type perform actions without returning values and can be used as statements:

```stan
void pretty_print_tri_lower(matrix x) {
  if (rows(x) == 0) {
    print("empty matrix");
    return;
  }
  print("rows=", rows(x), " cols=", cols(x));
  for (m in 1:rows(x)) {
    for (n in 1:m) {
      print("[", m, ",", n, "]=", x[m, n]);
    }
  }
}
```

Return statements in void functions have no arguments.

### Functions with Log Probability Access (_lp suffix)

Functions ending in `_lp` can use sampling statements and `target +=` statements, accessing the log probability accumulator. They're restricted to transformed parameters and model blocks:

```stan
vector center_lp(vector beta_raw, real mu, real sigma) {
  beta_raw ~ std_normal();
  sigma ~ cauchy(0, 5);
  mu ~ cauchy(0, 2.5);
  return sigma * beta_raw + mu;
}
```

### Jacobian Functions (_jacobian suffix)

Functions ending in `_jacobian` implement custom change-of-variables adjustments:

```stan
real my_upper_bound_jacobian(real x, real ub) {
  jacobian += x;
  return ub - exp(x);
}
```

### Random Number Generator Functions (_rng suffix)

Functions ending in `_rng` access built-in PRNG functions and must be used only in transformed data or generated quantities blocks (or in other `_rng` functions):

```stan
matrix predictors_rng(int N, int K) {
  matrix[N, K] x;
  for (n in 1:N) {
    x[n, 1] = 1.0;
    for (k in 2:K) {
      x[n, k] = normal_rng(0, 1);
    }
  }
  return x;
}
```

### Probability Functions (_lpdf and _lpmf)

Functions ending in `_lpdf` (density) or `_lpmf` (mass) with real return types become usable in distribution statements:

```stan
real unit_normal_lpdf(real y) {
  return normal_lpdf(y | 0, 1);
}
```

Then in the model block:
```stan
alpha ~ unit_normal();
```

is shorthand for:
```stan
target += unit_normal_lpdf(alpha);
```

The density/mass function distinction requires that `_lpdf` arguments are continuous while `_lpmf` arguments are discrete.

## Advanced Features

### Data-Only Function Arguments

Real-valued or container arguments can use the `data` qualifier to restrict inputs to data-only expressions:

```stan
real foo(real y, data real mu) {
  return -0.5 * (y - mu)^2;
}
```

This prevents parameters from being passed to these arguments, useful when calling ODE or algebraic solvers.

### Function Overloading

Multiple functions may share the same name with different argument counts or types. Stan resolves calls by selecting the signature requiring the fewest type promotions. When multiple signatures require equal promotions, an error occurs.

Integer-to-real promotion is preferred over integer-to-complex (which counts as two promotions).

### Recursive Functions

Stan supports recursion. Matrix power can be computed recursively:

```stan
matrix matrix_pow(matrix a, int n) {
  if (n == 0) {
    return diag_matrix(rep_vector(1, rows(a)));
  } else {
    return a * matrix_pow(a, n - 1);
  }
}
```

### Truncated Random Number Generation

Using inverse CDFs allows truncated variate generation. For a Weibull distribution truncated below at time t:

```stan
real weibull_lb_rng(real alpha, real sigma, real t) {
  real p = weibull_cdf(t | alpha, sigma);
  real u = uniform_rng(p, 1);
  real y = sigma * (-log1m(u))^inv(alpha);
  return y;
}
```

For truncation above and below a normal distribution:

```stan
real normal_lub_rng(real mu, real sigma, real lb, real ub) {
  real p_lb = normal_cdf(lb | mu, sigma);
  real p_ub = normal_cdf(ub | mu, sigma);
  real u = uniform_rng(p_lb, p_ub);
  real y = mu + sigma * inv_Phi(u);
  return y;
}
```

## Array Types

Array arguments follow specific syntax: `[ ]` for one-dimensional, `[ , ]` for two-dimensional, and so forth:

```stan
array[] real baz(array[,] real x);
```

## Documentation

Functions should be documented using comment blocks following Doxygen/Javadoc conventions:

```stan
/**
 * Return a data matrix of specified size with rows
 * corresponding to items and the first column filled
 * with the value 1 to represent the intercept.
 *
 * @param N Number of rows corresponding to data items
 * @param K Number of predictors, counting the intercept
 * @return Simulated predictor matrix.
 */
matrix predictors_rng(int N, int K) { ... }
```

The `@throws` tag documents exceptions raised by functions.

## Function Type Summary

Functions vary by return type (void or non-void) and by optional suffixes:

- **Void functions**: Used as statements only; return statements have no arguments
- **Non-void functions**: Used as expressions; require typed return statements
- **_lpdf/_lpmf functions**: Usable in distribution statements
- **_lp functions**: Access log probability; restricted to transformed parameters/model blocks
- **_rng functions**: Access PRNGs; restricted to generated quantities/transformed data

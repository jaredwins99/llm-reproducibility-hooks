# Stan Program Style Guide

## Overview

This guide outlines preferred styling conventions for Stan statistical programming language. The core principle emphasizes consistency above rigid adherence to specific rules.

## Key Style Recommendations

### Line Length
"Line lengths should not exceed 80 characters." This enables side-by-side window layouts and prevents wrapping in version control diffs.

### File Extensions
- `.stan` for model files
- `.stanfunctions` for function-only files (no wrapping in `functions{}` block needed)
- `.data.R` or `.R` for data dump files
- `.json` for JSON output

### Variable Naming
Follow C/C++ conventions with lowercase and underscores as separators. Preferred: `sigma_y` over `sigmay`, `sigmaY`, or `SigmaY`.

Exception: Size constants use single uppercase letters to match loop variables:
```stan
for (m in 1:M) {
  for (n in 1:N) {
     a[m, n] = ...
  }
}
```

### Local Variable Scope

Declare variables in blocks where they're used. This example demonstrates improving code clarity through local declaration:

```stan
// Better approach - loop-local declaration
model {
  for (n in 1:N) {
    real mu;
    mu = alpha * x[n] + beta;
    y[n] ~ normal(mu, sigma);
  }
}
```

Or eliminate the variable entirely by inlining:
```stan
model {
  for (n in 1:N) {
    y[n] ~ normal(alpha * x[n] + beta, sigma);
  }
}
```

For compound structures built component-by-component, declare outside loops to avoid repeated allocation:
```stan
model {
  vector[K] mu;
  for (n in 1:N) {
    for (k in 1:K) {
      mu[k] = // ...
    }
    y[n] ~ multi_normal(mu, Sigma);
  }
}
```

### Braces and Brackets

**Single-statement blocks** should use full bracketing with statements on separate lines:
```stan
for (n in 1:N) {
  y[n] ~ normal(mu, 1);
}
```

Omitting brackets creates danger—whitespace is ignored and parsers complete statements eagerly:
```stan
// Problematic - y[n] is outside the loop!
for (n in 1:N)
  z[n] ~ normal(nu, 1);
  y[n] ~ normal(mu, 1);
```

Exception: chained if-else structures with single conditionals can place the next `if` on the same line:
```stan
if (x) {
  // ...
} else if (y) {
  // ...
} else {
  // ...
}
```

**Parentheses in expressions** should be minimized. Operator precedence follows C++, R, Python, and Fortran conventions. Preferred: `a + b * c` over `a + (b * c)`.

**Opening braces** appear at line end, except for local scope-only blocks:
```stan
transformed parameters {
  real sigma;
  // ...
}
```

### Conditionals

Avoid real-valued conditions due to numerical precision issues. Use:
```stan
if (x != 0) { ...
```
rather than:
```stan
if (x) { ...
```

### Functions

Layout follows Java/C++ conventions:
```stan
real foo(real x, real y) {
  return sqrt(x * log(y));
}
```

For lengthy signatures, align arguments:
```stan
matrix
function_to_do_some_hairy_algebra(matrix thingamabob,
                                  vector doohickey2) {
  // ...body...
}
```

Document using Javadoc/Doxygen style:
```stan
/**
 * Return a data matrix of specified size with rows
 * corresponding to items and the first column filled
 * with the value 1 to represent the intercept and the
 * remaining columns randomly filled with unit-normal draws.
 *
 * @param N Number of rows correspond to data items
 * @param K Number of predictors, counting the intercept, per
 *          item.
 * @return Simulated predictor matrix.
 */
matrix predictors_rng(int N, int K) {
  // ...
}
```

### Whitespace Conventions

**Line breaks**: Each statement appears on its own line. Multiple variables of same type can combine: `real mu, sigma;`

**No tabs**: Use spaces only—tabs render inconsistently across systems.

**Indentation**: Use two-space indentation (C/C++ standard).

**Spacing rules**:
- Space after `if`: `if (x < y) {...` not `if(x < y){...`
- No space between function name and arguments: `normal(0, 1)` not `normal (0, 1)`
- Spaces around binary operators: `y[1] = x` not `y[1]=x`
- No spaces around unary operators: `-x`, `!y`
- Exception in type constraints: `real<lower=0> x;` (spaces still used around arithmetic in constraints)

**Breaking long expressions** should occur before operators, aligning for clarity:
```stan
vector[J] p_distance = Phi((distance_tolerance - overshot)
                           ./ ((x + overshot) * sigma_distance))
                       - Phi((-overshot)
                             ./ ((x + overshot) * sigma_distance));
```

For multi-argument functions, break after commas:
```stan
y[n] ~ normal(alpha + beta * x + gamma * y,
              pow(tau, -0.5));
```

**Commas**: Always followed by spaces in arguments, sequences, and declarations.

**Newlines**: Use Unix line-feed (LF) characters exclusively. Unix systems use `0x0A`; Windows uses carriage return + line-feed (`0x0D 0x0A`).

## Summary Principle

"The most important point of style is consistency." Departing from recommendations is acceptable if applied uniformly throughout projects and codebases.

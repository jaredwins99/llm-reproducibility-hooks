# Stan Reference Manual: Expressions

## Overview

An expression represents a syntactic unit denoting a value in Stan. The implementation type of every well-formed expression is statically determined at compile time based on variable and function types. If type cannot be determined statically, the Stan compiler reports the issue's location.

## Numeric Literals

### Integer Literals

Integer literals denote type `int` values written in base 10 without separators. A single negative sign is permitted.

Valid examples: `0, 1, -1, 256, -127098, 24567898765`

Integer literals must fall within valid bounds and cannot contain decimal points. Expressions like `1.` and `1.0` are type `real`.

### Real Literals

Numbers containing a period or scientific notation are type `real`. Scientific notation uses `e` or `E` with optional sign.

Valid examples: `0.0, 1.0, 3.14, -217.9387, 2.7e3, -2E-5, 1.23e+3`

### Imaginary Literals

A number followed by `i` denotes an imaginary number of type `complex`. The preceding value may be real or integer.

Valid examples: `1i, 2i, -325.786i, 1e10i, 2.87e-10i`

Note: `i` alone is invalid; use `1i` for the unit imaginary number.

### Complex Literals

Stan lacks direct complex literals but supports combining real/integer and imaginary literals through addition.

Valid examples: `1 + 2i, -3.2e9 + 1e10i`

## Variables

Variables consist of ASCII characters (letters, digits, underscores). They must start with a letter and cannot end with double underscores.

Valid identifiers: `a, a3, a_3, Sigma, my_cpp_style_variable, myCamelCaseVariable`

### Reserved Names

**Reserved words:** `for, in, while, repeat, until, if, then, else, true, false, target, struct, typedef, export, auto, extern, var, static, lower, upper, offset, multiplier`

**Type names (reserved):** `int, real, complex, vector, simplex, unit_vector, sum_to_zero_vector, sum_to_zero_matrix, ordered, positive_ordered, row_vector, matrix, cholesky_factor_corr, column_stochastic_matrix, row_stochastic_matrix, cholesky_factor_cov, corr_matrix, cov_matrix, array`

**Keywords/functions (reserved):** `print, reject, profile, fatal_error, target, jacobian`

**Block identifiers (reserved):** `functions, model, data, parameters, quantities, transformed, generated`

**Distribution suffixes (reserved):** Names ending in `_lpdf, _lpmf, _lcdf, _lccdf, _cdf, _ccdf, _lupdf, _lupmf`

**C++ keywords renamed with `_stan_` prefix:** `alignas, alignof, and, and_eq, asm, bitand, bitor, bool, case, catch, char, char16_t, char32_t, class, compl, const, constexpr, const_cast, decltype, default, delete, do, double, dynamic_cast, enum, explicit, float, friend, goto, inline, long, mutable, namespace, new, noexcept, not, not_eq, nullptr, operator, or, or_eq, private, protected, public, register, reinterpret_cast, short, signed, sizeof, static_assert, static_cast, switch, template, this, thread_local, throw, try, typeid, typename, union, unsigned, using, virtual, volatile, wchar_t, xor, xor_eq, fvar, STAN_MAJOR, STAN_MINOR, STAN_PATCH, STAN_MATH_MAJOR, STAN_MATH_MINOR, STAN_MATH_PATCH`

### Legal Characters

Only ASCII alphanumerics and underscores are permitted: `a-z` (97-122), `A-Z` (65-90), `0-9` (48-57), `_` (95)

## Container Expressions

### Vector Expressions

Square brackets around comma-separated expressions create row vector expressions:

```stan
row_vector[2] rv2 = [1, 2];
vector[3] v3 = [3, 4, 5]';
```

Expressions and variable names may be compound: `[2 * 3, 1 + 4]` or `[x, y]`

### Matrix Expressions

Matrix expressions use square brackets around comma-separated row vectors:

```stan
matrix[3, 2] m1 = [[1, 2], [3, 4], [5, 6]];
```

Valid row vector expressions work: variables, expressions, and literals.

```stan
vector[2] vX = [1, 10]';
row_vector[2] vY = [100, 1000];
matrix[3, 2] m2 = [vX', vY, [1, 2]];
```

### Complex Vector and Matrix Expressions

Complex vectors/matrices use identical syntax to real ones:

```stan
complex_vector[3] = [1 + 2i, 3 - 1.7i, 0]';
complex_row_vector[2] = [12, -2i];
complex_matrix[2, 3] = [[1 + 2i, 3 - 1.7i, 0],
                        [3.9 - 1.234i, 176i, 1 + 1i]];
```

### Empty Vectors and Matrices

Empty expressions `[]` are ambiguous and disallowed. Create empty containers using:

```stan
rep_vector(e, 0)      // empty vector (e: scalar real)
rep_matrix(e, 0, 0)   // empty matrix (e: scalar real)
```

### Array Expressions

Curly braces around comma-separated expressions produce array expressions:

```stan
array[3] int a = {1, 10, 100};
array[2, 3] int b = {{1, 2, 3}, {4, 5, 6}};
```

Multidimensional arrays may be formatted for clarity:

```stan
array[2, 3] int b = {{1, 2, 3},
                     {4, 5, 6}};
```

### Empty Arrays

Empty array expressions `{}` are disallowed due to type inference issues. Create empty arrays using:

```stan
rep_array(e, 0)       // empty real array
rep_array({123}, 0)   // empty 2D integer array
```

### Array Expression Types

Arrays may contain any expression type. When elements are the same type, the result is an array of that type:

```stan
vector[3] b;
vector[3] c;
array[2] vector[3] d = {b, c};
```

Mixed `int` and `real` expressions produce a real-valued array:

```stan
array[2] real b = {1, 1.9};
```

### Tuple Expressions and Types

Parentheses around comma-separated expressions construct tuples:

```stan
tuple(int, vector[3]) xy = (42, [1, 2.9, -1.3]');
```

Tuples must contain at least two elements. Python-style trailing commas are unsupported.

### Restrictions on Values

**Rectangular arrays only:** All Stan containers are rectangular (or higher-dimensional generalizations). Non-rectangular expressions cause compile-time or runtime errors:

```stan
{1, 2, 3}, {4, 5}  // compile-time error: size mismatch
```

**No empty array expressions:** Type cannot be inferred from empty braces.

**No zero-tuples or one-tuples:** Tuples must contain at least two elements. `()` is invalid; `(1)` is type `int`, not a tuple.

## Parentheses for Grouping

Parentheses explicitly group subexpressions. Only round parentheses are permitted; square brackets are reserved for indexing and curly braces for statements.

Expression `1 + 2 * 3` evaluates to 7 (standard precedence). Expression `(1 + 2) * 3` evaluates to 9.

## Arithmetic and Matrix Operations

### Basic Operations

For integer and real-valued expressions, Stan supports: addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`), modulus for integers (`%`), and unary negation.

Valid examples with integer `n, m` and real `x, y`:

```stan
3.0 + 0.14
-15
2 * 3 + 1
(x - y) / 2.0
(n * (n + 1)) / 2
x / n
m % n
```

### Matrix Operations

Negation, addition, subtraction, and multiplication extend to matrices, vectors, and row vectors. Transpose (apostrophe `'`) also applies to these types. Return types are the smallest statically guaranteed types.

For `y, mu` type `vector` and `Sigma` type `matrix`, the expression `(y - mu)' * Sigma * (y - mu)` is valid type `real`.

### Elementwise Operations

Elementwise multiplication (`.*`) and division (`./`) are supported:

```stan
vector[N] a;
vector[N] b;
vector[N] c;

c = a .* b;   // equivalent to loop
```

Produces same result as:

```stan
for (n in 1:N)
  c[n] = a[n] * b[n];
```

### Exponentiation

Exponentiation (`^`) applies to integer and real values, always returning real:

```stan
3 ^ 2
3.0 ^ -2
3.0 ^ 0.14
x ^ n
n ^ x
n ^ m
x ^ y
```

Exponentiation is right associative: `2 ^ 3 ^ 4` equals `2 ^ (3 ^ 4)`.

### Operator Precedence and Associativity

| Operator | Precedence | Associativity | Type | Description |
|----------|-----------|--------------|------|------------|
| `? ~ :` | 10 | right | ternary infix | conditional |
| `\|\|` | 9 | left | binary infix | logical or |
| `&&` | 8 | left | binary infix | logical and |
| `==` | 7 | left | binary infix | equality |
| `!=` | 7 | left | binary infix | inequality |
| `<` | 6 | left | binary infix | less than |
| `<=` | 6 | left | binary infix | less than or equal |
| `>` | 6 | left | binary infix | greater than |
| `>=` | 6 | left | binary infix | greater than or equal |
| `+` | 5 | left | binary infix | addition |
| `-` | 5 | left | binary infix | subtraction |
| `*` | 4 | left | binary infix | multiplication |
| `.*` | 4 | left | binary infix | elementwise multiplication |
| `/` | 4 | left | binary infix | division |
| `./` | 4 | left | binary infix | elementwise division |
| `%` | 4 | left | binary infix | modulus |
| `\` | 3 | left | binary infix | left division |
| `%/%` | 3 | left | binary infix | integer division |
| `!` | 2 | n/a | unary prefix | logical negation |
| `-` | 2 | n/a | unary prefix | negation |
| `+` | 2 | n/a | unary prefix | promotion |
| `^` | 1 | right | binary infix | exponentiation |
| `.^` | 1 | right | binary infix | elementwise exponentiation |
| `'` | 0 | n/a | unary postfix | transposition |
| `()` | 0 | n/a | prefix, wrap | function application |
| `[]` | 0 | left | prefix, wrap | array/matrix indexing |

Left associativity means `a + b + c` parses as `(a + b) + c`. Higher precedence binds tighter, so `a * b + c` parses as `(a * b) + c`. For vectors/matrices, `-u'` parses as `-(u')`, and `u * v'` as `u * (v')`. For integers/reals, `-n ^ 3` parses as `-(n ^ 3)`.

## Conditional Operator

### Syntax

The ternary conditional operator takes three arguments with mixed syntax:

```stan
a ? b : c
```

Where `a` is type `int` and `b, c` can be converted to each other. The result is promoted type of `b` and `c`. Allowed promotions: `int` -> `real` -> `complex`.

### Precedence and Associativity

Conditional operator is the most loosely binding, requiring minimal parentheses:

```stan
a > 0 || b < 0 ? c + d : e - f
```

Equivalent to:

```stan
(a > 0 || b < 0) ? (c + d) : (e - f)
```

Right associative parsing:

```stan
a ? b : c ? d : e
```

Equivalent to:

```stan
a ? b : (c ? d : e)
```

### Semantics

The first argument must be an integer expression. The second argument returns if the condition evaluates to non-zero (true); the third returns if zero (false).

**Lazy evaluation:** Only the returned subexpression evaluates, not the alternative. This provides performance benefits by avoiding unnecessary derivative calculations.

**Promotion to parameter:** If one return expression is data-only and the other contains parameters, the conditional operator promotes the data value to a parameter value. This can cause unnecessary derivative work. For efficiency, use `if-then` statements instead:

```stan
// Less efficient
y ~ normal(cond ? x : z, sigma);

// More efficient
if (cond)
  y ~ normal(x, sigma);
else
  y ~ normal(z, sigma);
```

## Indexing

Stan arrays, matrices, vectors, and row vectors use array-like notation. If `x` is type `array[] real`:

```stan
x[1]  // first element
```

Subscripting has higher precedence than arithmetic, so `alpha * x[1]` equals `alpha * (x[1])`.

Multiple subscripts in a single bracket pair access multidimensional structures. For type `array[,] real`:

```stan
x[2, 501]  // element at row 2, column 501
```

### Accessing Subarrays

Subscripting returns subarrays. For type `array[,,] real`:

```stan
x[2]          // type: array[,] real
x[2, 3]       // type: array[] real
x[2, 3, 4]    // type: real
```

The expressions `x[2, 3]` and `x[2][3]` are equivalent.

### Accessing Matrix Rows

For matrix `Sigma`:

```stan
Sigma[1]  // first row (type: row_vector)
```

### Mixing Array and Vector/Matrix Indexes

For type `array[,] matrix` variable `m`:

```stan
m[1]          // type: array[] matrix (first row of array)
m[1, 2]       // type: matrix
m[1, 2, 3]    // type: row_vector (row 3 of matrix at m[1,2])
m[1, 2, 3, 4] // type: real (element at m[1,2][3,4])
```

## Multiple Indexing and Range Indexing

Stan supports multiple indexing beyond single integers: integer arrays, lower bounds, upper bounds, ranges, and "all" shorthand. Upper and lower bounds can be expressions evaluating to integers.

### Indexing Options

| Index Type | Example | Value |
|-----------|---------|-------|
| integer | `a[11]` | value at index 11 |
| integer array | `a[ii]` | `a[ii[1]], ..., a[ii[K]]` |
| lower bound | `a[3:]` | `a[3], ..., a[N]` |
| upper bound | `a[:5]` | `a[1], ..., a[5]` |
| range | `a[2:7]` | `a[2], ..., a[7]` |
| empty range | `a[7:2]` | `[]` |
| expression range | `a[5-3:5+2]` | `a[2], ..., a[7]` |
| all | `a[:]` | `a[1], ..., a[N]` |
| all | `a[]` | `a[1], ..., a[N]` |

Range indexing with `:` produces increasing sequences only. For decreasing sequences, construct an integer array:

```stan
array[6] int ii = reverse(linspaced_int_array(6, 2, 7));
a[ii]  // evaluates to a[7], ..., a[2]
```

### Multiple Index Semantics

The fundamental rule: if `idxs` is a multiple index, it produces an indexable position in the result.

```stan
a[idxs, ...][i, ...] = a[idxs[i], ...][...]
```

Single index `idx` reduces dimensionality:

```stan
a[idx, ...] = a[idx][...]
```

### Matrix Indexing Rules

Matrices have special rules based on single vs. multiple indexes:

| Example | Row Index | Column Index | Result Type |
|---------|-----------|--------------|-------------|
| `a[i]` | single | n/a | row_vector |
| `a[is]` | multiple | n/a | matrix |
| `a[i, j]` | single | single | real |
| `a[i, js]` | single | multiple | row_vector |
| `a[is, j]` | multiple | single | vector |
| `a[is, js]` | multiple | multiple | matrix |

Evaluation respects distributivity:

```stan
m[idxs1, idxs2][i, j] = m[idxs1[i], idxs2[j]]
m[idxs, idx][j] = m[idxs[j], idx]
m[idx, idxs][j] = m[idx, idxs[j]]
```

## Function Application

Stan provides built-in mathematical and statistical functions. Function application consists of a function name followed by zero or more argument expressions.

```stan
log(2.0)  // type: real
```

Function application has higher precedence than operators, so `y + log(x)` equals `y + (log(x))`.

### Type Signatures and Result Type Inference

Each function has a type signature determining allowable argument types and return type:

```stan
real log(real);
real lmultiply(real, real);
real mean(array[] real);
real mean(vector);
```

Functions are uniquely determined by name and argument types. Different argument sequences create different functions. Type inference proceeds compositionally from subexpression types.

### Constants

Constants are nullary (no-argument) functions. Mathematical constants include:

```stan
pi()
e()
```

### Type Promotion and Function Resolution

Function resolution follows C++'s scheme: call the function requiring minimum type promotions.

With signatures:

```stan
real foo(real, real);
int foo(int, int);
```

The expression `foo(1.0, 1.0)` calls `foo(real, real)` (type: real). The expression `foo(1, 1)` calls `foo(int, int)` (type: int) requiring zero promotions. The expression `foo(1, 1.0)` calls `foo(real, real)` after promoting the integer (type: real).

Ambiguous calls cause compiler errors. With signatures:

```stan
real bar(real, int);
real bar(int, real);
```

`bar(1.0, 1.0)` is illegal (real values don't demote to int). `bar(1, 1)` is illegal (ambiguous: both require one promotion).

### Random-Number Generating Functions

Most distributions have corresponding RNG functions suffixed with `_rng`. For normal distribution:

```stan
normal_rng(0, 1)  // generates univariate normal variate
```

**Restrictions:** RNGs are restricted to `transformed data` and `generated quantities` blocks, and within user-defined function bodies ending in `_rng`.

**Posterior predictive checking:** RNGs enable simulation and Bayesian posterior predictive checks, comparing simulated data generated using model parameters against observed data to assess model suitability.

## Type Inference

Stan is strongly statically typed. Expression implementation types resolve at compile time.

### Implementation Types

Primitive implementation types:

```
int, real, complex, vector, row_vector, matrix,
complex_vector, complex_row_vector, complex_matrix
```

Every declared type maps to a primitive implementation type:

| Type | Primitive |
|------|-----------|
| `int` | `int` |
| `real` | `real` |
| `vector` | `vector` |
| `simplex` | `vector` |
| `unit_vector` | `vector` |
| `sum_to_zero_vector` | `vector` |
| `ordered` | `vector` |
| `positive_ordered` | `vector` |
| `row_vector` | `row_vector` |
| `matrix` | `matrix` |
| `cov_matrix` | `matrix` |
| `corr_matrix` | `matrix` |
| `cholesky_factor_cov` | `matrix` |
| `cholesky_factor_corr` | `matrix` |
| `column_stochastic_matrix` | `matrix` |
| `row_stochastic_matrix` | `matrix` |
| `sum_to_zero_matrix` | `matrix` |
| `complex_vector` | `complex_vector` |
| `complex_row_vector` | `complex_row_vector` |
| `complex_matrix` | `complex_matrix` |

Complete implementation types consist of primitive type plus integer array dimensionality >= 0. Examples: `array[] real` (dimensionality 1), `int` (dimensionality 0), `array[,,] int` (dimensionality 3).

Three-dimensional array of matrices:

```stan
array[I, J, K] matrix[M, N] a;  // indexed as a[i, j, k, m, n]
a[i, j, k]    // type: matrix
a[i, j, k, m] // type: row_vector
```

### Type Inference Rules

Inference rules determine expression implementation types from variable declarations, working bottom-up from literal and variable expressions to complex ones.

### Promotion

Two basic promotion rules:

1. `int` types may promote to `real`
2. `real` types may promote to `complex`

Plus transitivity: if `U` promotes to `V` and `V` to `T`, then `U` promotes to `T`.

Covariant typing for containers: a container of type `U` promotes to a same-shape container of type `T` if `U` promotes to `T`:

4. `vector` may promote to `complex_vector`
5. `row_vector` may promote to `complex_row_vector`
6. `matrix` may promote to `complex_matrix`

Arrays: `array[...] U` may promote to `array[...] T` if `U` promotes to `T`. Example: `array[,] int` may be used where `array[,] real` is required.

Tuples: `tuple(U1, ..., UN)` may promote to `tuple(T1, ..., TN)` if every `Un` promotes to `Tn`.

### Literals, Variables, and Indexing Rules

Integer literals (e.g., `42`) are type `int`. Real literals (e.g., `42.0`) are type `real`. Imaginary literals (e.g., `-17i`) are type `complex`.

Variable type is determined by declaration. Loop variable type is `int`.

For indexing, if `e` has type `array[i1, i2, ..., iN] T` and `k, i1, ..., iN` are type `int`, then `e[k]` is type `array[i2, ..., iN] T`. If `e` has type `array[i] T`, then `e[k]` is type `T`.

For vectors/row vectors (dimensionality 0): `e[i]` is type `real`.
For matrices: `e[i]` is type `row_vector`.
For complex vectors/row vectors: `e[i]` is type `complex`.
For complex matrices: `e[i]` is type `complex_row_vector`.

### Function Application Type Inference

If `f` is a function name and `e1,...,eN` are expressions, `f(e1,...,eN)` has type determined by the function signature for `f` given those arguments. All promotion rules apply during function matching.

Matrix operations return the lowest inferable type. Example: `row_vector * vector` returns `real`.

## Higher-Order Functions

Several expression constructions act as higher-order functions. The `integrate_ode_rk45` function integrates differential equations:

```stan
functions {
  array[] real foo(real t, array[] real y, array[] real theta,
                   array[] real x_r, array[] real x_i) {
    // ...
  }
}
// ...
int<lower=1> T;
array[2] real y0;
real t0;
array[T] real ts;
array[1] real theta;
array[0] real x_r;
array[0] int x_i;
// ...
array[T, 2] real y_hat = integrate_ode_rk45(foo, y0, t0,
                                            ts, theta, x_r, x_i);
```

### Higher-Order Functions Table

| Function | Parameter/Data Args | Data Args | Return |
|----------|-------------------|-----------|--------|
| `algebra_solver` | `vector, vector` | `array[] real, array[] real` | `vector` |
| `algebra_solver_newton` | `vector, vector` | `array[] real, array[] real` | `vector` |
| `integrate_1d` | `real, real, array[] real` | `array[] real, array[] real` | `real` |
| `integrate_ode_X` | `real, array[] real, array[] real` | `array[] real, array[] real` | `array[] real` |
| `map_rect` | `vector, vector` | `array[] real, array[] real` | `vector` |

### Variadic Higher-Order Functions

| Function | Restricted Args | Return |
|----------|-----------------|--------|
| `solve_X` | `vector` | `vector` |
| `ode_X` | `vector, real, array[] real` | `vector[]` |
| `reduce_sum` | `array[] T, T1, T2` | `real` |

Example using `ode_rk45`:

```stan
functions {
  vector foo(real t, vector y, real theta, vector beta,
             array[] real x_i, int index) {
    // ...
  }
}
// ...
int<lower=1> T;
vector[2] y0;
real t0;
array[T] real ts;
real theta;
vector[7] beta;
array[10] int x_i;
int index;
// ...
vector[2] y_hat[T] = ode_rk45(foo, y0, t0, ts, theta,
                              beta, x_i, index);
```

### Functions Passed by Reference

Function arguments to higher-order functions must be user-defined or built-in function names (no quotes needed).

### Data-Restricted Arguments

Some higher-order function arguments must be data-only: containing only data variables, transformed data variables, or literals; may apply arbitrary functions to these, but must not contain parameters, transformed parameters, or local variables from other blocks. User-defined functions may use the `data` qualifier to restrict argument types.

## Chain Rule and Derivatives

Hamiltonian Monte Carlo samplers and BFGS optimizers use log probability gradients. Derivatives evaluate via mechanistic chain rule application on floating-point arithmetic.

### Errors Due to Chain Rule

Problematic models include expressions like:

```stan
parameters {
  real x;
}
model {
  x ~ normal(sqrt(x - x), 1);
}
```

Although algebraically `sqrt(x - x)` reduces to 0, mechanistic chain rule application produces:

d/dx sqrt(x - x) = 1 / (2 * sqrt(x - x)) * d/dx(x - x) = 1/0 * (1 - 1) = infinity * 0 = NaN

The subtraction introduces 0 into numerator and denominator, producing not-a-number. Prevention requires careful algebraic reduction before model specification.

### Diagnosing Problems with Derivatives

Use the test-gradient diagnostic option for samplers or optimizers (available in Stan and RStan, though slow due to finite-difference comparison). For CmdStan example:

```
> ./sqrt-x-minus-x diagnose test=gradient
```

Output shows:

```
TEST GRADIENT MODE

Log probability=-0.393734

param idx           value           model     finite diff           error
        0       -0.887393             nan               0             nan
```

Finite differences compute correct gradient 0, but automatic differentiation follows chain rule producing not-a-number.

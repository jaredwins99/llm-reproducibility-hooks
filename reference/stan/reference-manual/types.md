# Stan Data Types and Declarations - Complete Content

## Overview

Stan requires explicit declaration of all variable data types, following the principle of strong, static typing similar to C++. This approach offers three primary benefits:

1. **Clarity**: Declared intent makes programs easier to comprehend and maintain
2. **Early Error Detection**: Type errors are caught at compile time rather than runtime
3. **Constraint Validation**: Constrained types catch data and value errors immediately

"Strong typing disallows assigning the same variable to objects of different types at different points in the program or in different invocations."

## Primitive Data Types

Stan provides two primitive scalar types:
- `int`: Integer values (32-bit, range +/-2^31)
- `real`: Continuous floating-point values (64-bit IEEE 754)
- `complex`: Complex numbers with real and imaginary components

### Integer Characteristics

The maximum value that can be represented as an integer is 2^31 - 1; the minimum value is -(2^31).

Integer arithmetic supports addition, subtraction, and multiplication with truncated division.

### Real Number Characteristics

Stan uses 64-bit (8-byte) floating point representations of real numbers. Stan roughly follows the IEEE 754 standard for floating-point computation.

The range is approximately +/-2^1022 (+/-10^307), with roughly 15 decimal digits of accuracy. Special values include:
- Not-a-number (NaN) for error conditions
- Positive infinity for overflow
- Negative infinity for underflow

### Promoting Integers to Reals

Stan automatically promotes integer values to real values if necessary, but does not automatically demote real values to integers.

## Complex Numbers

Complex numbers contain both real and imaginary components (both `real` type):

```stan
complex z = 2 - 1.3i;
real re = get_real(z);  // re has value 2.0
real im = get_imag(z);  // im has value -1.3
```

Construction using the `to_complex()` function:

```stan
vector[K] re;
vector[K] im;
for (k in 1:K) {
  complex z = to_complex(re[k], im[k]);
}
```

Real values promote to complex with imaginary component set to zero.

## Scalar Variable Declarations

### Unconstrained Types

**Integer:**
```stan
int N;
```

**Real:**
```stan
real theta;
```

**Complex:**
```stan
complex z;
```

### Constrained Integer

```stan
int<lower=1> N;           // positive integer
int<lower=0, upper=1> cond;  // binary (0 or 1)
```

### Constrained Real

```stan
real<lower=0> sigma;      // non-negative
real<upper=-1> x;         // less than or equal to -1
real<lower=-1, upper=1> rho;  // bounded interval
```

### Affinely Transformed Real

Real variables may be transformed using offset mu and multiplier sigma:

```stan
real<offset=1> x;
real<multiplier=2> x;
real<offset=1, multiplier=2> x;
```

Example non-centered parameterization:

```stan
parameters {
  real<offset=mu, multiplier=sigma> x;
}
model {
  x ~ normal(mu, sigma);
}
```

### Expressions as Bounds

Bounds may be arbitrary expressions using previously declared variables:

```stan
data {
  real lb;
}
parameters {
  real<lower=lb> phi;
}
```

Or with functions:

```stan
data {
  int<lower=1> N;
  array[N] real y;
}
parameters {
  real<lower=min(y), upper=max(y)> phi;
}
```

### Optional Variables

Variables may be conditionally sized:

```stan
data {
  int<lower=0, upper=1> include_alpha;
}
parameters {
  vector[include_alpha ? N : 0] alpha;
}
```

## Vector and Matrix Types

Stan distinguishes between vectors, matrices, and arrays. Vectors are intrinsically one-dimensional collections of real or complex values, whereas matrices are intrinsically two dimensional.

Three situations require vectors/matrices specifically:
- Matrix arithmetic operations
- Linear algebra functions
- Multivariate function parameters

**Indexing convention:** Vectors and matrices, as well as arrays, are indexed starting from one (1) in Stan.

### Vectors

Column vectors declared with size:

```stan
vector[3] u;
vector<lower=0>[3] u;
vector<offset=42, multiplier=3>[3] u;
```

### Complex Vectors

```stan
complex_vector[3] v;
```

### Unit Simplexes

Vectors with non-negative values summing to 1:

```stan
simplex[5] theta;
```

Unit simplexes are most often used as parameters in categorical or multinomial distributions.

### Stochastic Matrices

Matrices where each column (or row) is a unit simplex:

```stan
column_stochastic_matrix[3, 4] theta;  // 3 rows, 4 columns
row_stochastic_matrix[3, 4] theta;    // each row sums to 1
```

### Unit Vectors

Vectors with norm equal to one:

```stan
unit_vector[5] theta;
```

### Vectors That Sum to Zero

Zero-sum constraints with N-1 degrees of freedom:

```stan
sum_to_zero_vector[5] beta;
```

### Ordered Vectors

Entries sorted in ascending order:

```stan
ordered[5] c;
positive_ordered[5] d;
```

### Row Vectors

```stan
row_vector[1093] u;
row_vector<lower=-1, upper=1>[10] u;
complex_row_vector[12] v;
```

### Matrices

```stan
matrix[3, 3] A;
matrix[M, N] B;
matrix<upper=0>[3, 4] B;
matrix<multiplier=5>[3, 4] B;
```

Assigning to matrix rows:

```stan
matrix[M, N] a;
row_vector[N] b;
a[1] = b;  // assigns row vector to first row
```

### Complex Matrices

```stan
complex_matrix[3, 3] C;
```

### Covariance Matrices

Symmetric, positive definite matrices:

```stan
cov_matrix[K] Sigma;
```

### Correlation Matrices

Symmetric, positive definite with unit diagonal:

```stan
corr_matrix[3] Omega;
```

### Cholesky Factors

**Covariance:**
```stan
cholesky_factor_cov[4] L;
cholesky_factor_cov[M, N] L;  // general rectangular form
```

**Correlation:**
```stan
cholesky_factor_corr[K] L;
```

A Cholesky factor L is an M x N lower-triangular matrix with a strictly positive diagonal.

### Matrices That Sum to Zero

```stan
sum_to_zero_matrix[5, 4] beta;
```

### Accessing Elements

```stan
vector[N] v;
real x = v[2];

matrix[M, N] m;
real x = m[2, 3];
row_vector[N] r = m[2];  // single index returns row

complex_matrix[M, N] m;
complex_vector[M] v = m[ , 2];  // column access
```

## Array Data Types

Stan supports arrays of arbitrary dimension. The values in an array can be any type, so that arrays may contain values that are simple reals or integers, vectors, matrices, or other arrays.

### Declaration

```stan
array[5] int n;
array[3, 4] complex a;
array[5, 4, 2] real<lower=0> z;
array[3] vector[7] mu;
array[15, 12] complex_matrix[7, 2] mu;
array[2, 3, 4] cholesky_factor_cov[5, 6] mu;
```

### Accessing Elements

```stan
array[3, 4] vector[5] a;
vector[5] c = a[1, 3];

array[3, 4] matrix[6, 5] d;
row_vector[5] g = d[1, 3, 2];
```

### Partial Assignment

```stan
array[I, J, K] real x;
array[J, K] real y;
x[1] = y;  // sizes must match
```

### Mixing Types

Arrays, row vectors, column vectors and matrices are not interchangeable in Stan.

Illegal assignments:
```stan
array[4] real a;
vector[4] b;
a = b;  // illegal
```

Row and column vectors:
```stan
vector[4] b;
row_vector[4] c;
b = c;  // illegal
```

### Size Zero Arrays

```stan
array[3, 0] real a;   // overall size is zero
array[0, 3] real b;   // overall size is zero, no legal indexing
```

## Tuple Data Type

Stan supports tuples of arbitrary size. The values in a tuple can be of arbitrary type.

### Declaration

```stan
tuple(real, array[5] int) xi;
tuple(int, vector[3], complex) abc;
tuple(int, tuple(real, complex)) x;
```

Tuples must have at least two entries. Constraints are allowed:

```stan
tuple(real<lower=0>, real<lower=0, upper=1>) sigma_theta;
```

### Accessing Elements

Using integer literal indices:

```stan
tuple(int, vector[3], complex) abc;
int first = abc.1;
vector[3] vec = abc.2;
complex z = abc.3;
```

### Assigning Elements

```stan
tuple(int, real) ab;
ab.1 = 123;
ab.2 = 12.9;
```

### Unpacking Assignment

```stan
tuple(int, (real, real), complex) T;
int i;
real x, y;
complex z;
(i, (x, y), z) = T;
```

The left hand side must match in size the tuple on the right. Additionally, the same variable may not appear more than once in the left hand side.

## Type Information

### Sizes Are Not Part of Type

The size associated with a given variable is not part of its data type.

Sizes are determined dynamically (at run time) and thus cannot be type-checked statically.

### Constraints Are Not Part of Type

Like sizes, constraints are not treated as part of a variable's type.

A covariance matrix may be assigned to a regular matrix and vice versa:

```stan
cov_matrix[K] Sigma;
matrix[K, K] A = Sigma;  // legal
```

## Variable Declaration

All variables must be explicitly declared:

```stan
int N;
vector[N] y;
array[5] matrix[3, 4] A;
```

The size of top-level variables in the parameters, transformed parameters, and generated quantities must remain constant across all iterations, therefore only data variables can be used in top-level size declarations.

Top-level block variables require sizes and may have constraints. Local variables include sizes but no constraints. Function parameters exclude both sizes and constraints.

## Compound Declaration and Definition

Variables may be declared and initialized simultaneously:

```stan
int N = 5;
real sum = 0;  // int promoted to real
matrix[3, 2] a = 0.5 * (b + c);
complex z = 2 + 3i;
```

The type of the expression on the right-hand side of the assignment must be assignable to the type of the variable being declared.

## Multiple Variable Declaration

Declare multiple variables of the same type:

```stan
real x, y;
real x = 3, y = 5.6;
real<lower=0> x, y;
```

All declarations on the same line must be of the same type.

## Type Summary Table

Stan provides a comprehensive type system with unconstrained function arguments, sized local variables, and constrained block variables:

| Function Argument | Local (unconstrained) | Block (constrained) |
|---|---|---|
| `int` | `int` | `int`, `int<lower=L>`, `int<upper=U>`, etc. |
| `real` | `real` | `real<lower=L>`, `real<upper=U>`, etc. |
| `complex` | `complex` | `complex` |
| `vector` | `vector[N]` | `vector[N]<...>`, `ordered[N]`, `positive_ordered[N]`, `simplex[N]`, `unit_vector[N]`, `sum_to_zero_vector[N]` |
| `row_vector` | `row_vector[N]` | `row_vector[N]<...>` |
| `matrix` | `matrix[M, N]` | `matrix[M, N]<...>`, `column_stochastic_matrix[M, N]`, `row_stochastic_matrix[M, N]`, `sum_to_zero_matrix[M, N]`, `corr_matrix[K]`, `cov_matrix[K]`, `cholesky_factor_corr[K]`, `cholesky_factor_cov[K]` |
| `complex_vector` | `complex_vector[M]` | `complex_vector[M]` |
| `complex_row_vector` | `complex_row_vector[N]` | `complex_row_vector[N]` |
| `complex_matrix` | `complex_matrix[M, N]` | `complex_matrix[M, N]` |

## Key Principles

The model must have support (non-zero density, equivalently finite log density) at parameter values that satisfy the declared constraints.

Violating this principle causes pathologies including just getting stuck, failure to initialize, excessive Metropolis rejection, or biased draws due to inability to explore the tails of the distribution.

# Stan Matrix Operations Reference

## Overview

This page documents Stan's built-in matrix operation functions from version 2.38. The content covers sizing functions, arithmetic operators, linear algebra, decompositions, and specialized matrix operations.

## Matrix Size Functions

Stan provides integer-valued functions for determining matrix dimensions:

- **`num_elements()`** - Total elements in vectors/matrices
- **`rows()`** - Row count
- **`cols()`** - Column count
- **`size()`** - Element count (available since 2.26)

## Arithmetic Operations

### Basic Operators

"The negation of the vector x" and similar operations apply to matrices and row vectors. Addition, subtraction, and multiplication follow standard linear algebra rules for compatible dimensions.

Scalar broadcasting is supported: "The result of adding y to every entry in the vector x."

### Elementwise Operations

The `.*` operator performs elementwise multiplication. The `./` operator divides elements. The `.^` operator raises elements to powers (available since 2.24).

## Transposition

"The transpose of the matrix x, written as `x'`" converts rows to columns. Vectors transpose to row vectors and vice versa.

## Specialized Products

Key functions include:

- **`dot_product()`** - Inner product
- **`columns_dot_product()`** - Dot products of columns
- **`rows_dot_product()`** - Dot products of rows
- **`tcrossprod()`** - "The product of x postmultiplied by its own transpose"
- **`crossprod()`** - "The product of x premultiplied by its own transpose"
- **`quad_form()`** - Quadratic forms
- **`quad_form_diag()`** - Diagonal quadratic forms
- **`quad_form_sym()`** - Symmetric quadratic forms with validation

## Reductions

Functions that reduce matrices to scalars:

- **`log_sum_exp()`** - "The natural logarithm of the sum of the exponentials"
- **`min()`/`max()`** - Extrema
- **`sum()`/`prod()`** - Summation and products
- **`mean()`**, **`variance()`**, **`sd()`** - Sample statistics
- **`quantile()`** - Sample quantiles (available since 2.27)

## Broadcasting Functions

Container construction functions:

- **`rep_vector()`**, **`rep_row_vector()`**, **`rep_matrix()`** - Create structures by copying values
- **`linspaced_vector()`**, **`linspaced_array()`** - Equidistantly-spaced elements
- **`ones_vector()`**, **`zeros_vector()`** - Constant-filled containers
- **`one_hot_vector()`** - One-hot encoding
- **`uniform_simplex()`** - "Create an `n`-dimensional simplex with elements `vector[i] = 1 / n`"

## Slicing and Blocking

- **`col()`**, **`row()`** - Extract columns/rows
- **`block()`** - Extract submatrices
- **`sub_col()`**, **`sub_row()`** - Extract slices
- **`head()`**, **`tail()`**, **`segment()`** - Extract portions of arrays/vectors
- **`append_col()`**, **`append_row()`** - Concatenate matrices

## Diagonal Operations

- **`diagonal()`** - Extract diagonal
- **`diag_matrix()`** - Create diagonal matrix from vector
- **`add_diag()`** - Add values to diagonal (available since 2.21)
- **`identity_matrix()`** - Create identity matrices (available since 2.26)
- **`diag_pre_multiply()`**, **`diag_post_multiply()`** - Multiply by diagonal matrices

## Softmax Functions

"The softmax of x" maps vectors to simplexes. "The natural logarithm of the softmax of x" provides numerically stable computation via "log softmax(y) = y - log_sum_exp(y)."

## Cumulative Operations

**`cumulative_sum()`** "computes the sequence y_1,...,y_n, where y_n = sum(m=1 to n) x_m."

## Gaussian Process Kernels

Covariance functions for GPs with various kernels:

- **Exponentiated Quadratic** - "sigma^2 exp(-|x_i - x_j|^2/(2l^2))"
- **Dot Product** - "sigma_0^2 + x_i^T x_j"
- **Exponential** - "sigma^2 exp(-|x_i - x_j|/l)"
- **Matern 3/2** and **Matern 5/2**
- **Periodic** - "sigma^2 exp(-2sin^2(pi|x_i - x_j|/p)/l^2)"

## Linear Algebra

### Matrix Division

Preferred over explicit inversion: "The right division of b by A; equivalently `b * inverse(A)`" and left division operations using `\` operator.

### Specialized Solvers

- **`mdivide_left_tri_low()`**, **`mdivide_right_tri_low()`** - Lower triangular solving
- **`mdivide_left_spd()`**, **`mdivide_right_spd()`** - Symmetric positive-definite solving

### Decompositions

- **`cholesky_decompose()`** - "The lower-triangular Cholesky factor"
- **`qr_thin_Q()`**, **`qr_thin_R()`** - Thin QR decomposition
- **`eigenvalues_sym()`**, **`eigenvectors_sym()`** - Symmetric eigendecomposition
- **`singular_values()`**, **`svd_U()`**, **`svd_V()`** - Singular value decomposition
- **`eigendecompose_sym()`** - Combined eigendecomposition (available since 2.33)

### Other Linear Algebra

- **`trace()`** - Matrix trace
- **`determinant()`**, **`log_determinant()`** - Determinants
- **`inverse()`**, **`inverse_spd()`**, **`chol2inv()`** - Matrix inversion
- **`generalized_inverse()`** - Pseudoinverse (available since 2.26)
- **`matrix_exp()`** - Matrix exponential (available since 2.13)
- **`matrix_power()`** - Integer powers (available since 2.24)

## Sorting and Ordering

- **`sort_asc()`**, **`sort_desc()`** - Sort elements
- **`sort_indices_asc()`**, **`sort_indices_desc()`** - Sorting permutations
- **`rank()`** - "Number of components of v less than v[s]"
- **`reverse()`** - Reverse element order (available since 2.23)

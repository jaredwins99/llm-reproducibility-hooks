# Complex Matrix Operations - Stan Functions Reference

## Overview

This documentation covers complex matrix operations in Stan version 2.38. The page provides comprehensive function signatures and descriptions for complex number computations across vectors, matrices, and row vectors.

## Complex Promotion

Stan supports automatic type promotion following these rules:

- `int` promotes to `real`
- `real` promotes to `complex`
- `vector` promotes to `complex_vector`
- `row_vector` promotes to `complex_row_vector`
- `matrix` promotes to `complex_matrix`
- Promotion is transitive and covariant with arrays

When functions are called, the signature requiring the fewest promotions is selected. Complex function signatures list only fully complex types; other combinations are implied through promotion.

## Integer-Valued Size Functions

Functions returning dimensions:

- `num_elements(complex_vector|complex_row_vector|complex_matrix)` - total element count
- `rows(complex_vector|complex_row_vector|complex_matrix)` - row count
- `cols(complex_vector|complex_row_vector|complex_matrix)` - column count
- `size(complex_vector|complex_row_vector|complex_matrix)` - element count

All available since version 2.30.

## Arithmetic Operators

### Negation
- `operator-(complex_vector|complex_row_vector|complex_matrix)` - negation
- Vectorized negation for nested arrays

### Addition/Subtraction
- `operator+(complex_vector, complex_vector)` -> `complex_vector`
- `operator+(complex_row_vector, complex_row_vector)` -> `complex_row_vector`
- `operator+(complex_matrix, complex_matrix)` -> `complex_matrix`
- Subtraction equivalents with `operator-`
- Broadcast versions with scalar operands

### Multiplication
- Scalar multiplication: `complex * complex_vector|complex_row_vector|complex_matrix`
- Vector/row vector outer product: `complex_vector * complex_row_vector` -> `complex_matrix`
- Matrix-vector products: `complex_matrix * complex_vector` -> `complex_vector`
- Matrix-matrix products: `complex_matrix * complex_matrix` -> `complex_matrix`
- Row vector-matrix: `complex_row_vector * complex_matrix` -> `complex_row_vector`

### Division
- Broadcast division: `complex_vector|complex_row_vector|complex_matrix / complex`

## Transposition

- `operator'(complex_matrix)` -> `complex_matrix`
- `operator'(complex_vector)` -> `complex_row_vector`
- `operator'(complex_row_vector)` -> `complex_vector`

## Elementwise Functions

- `operator.*(complex_vector, complex_vector)` - elementwise multiplication
- `operator./(complex_vector, complex_vector)` - elementwise division
- Broadcast versions with scalar operands
- `operator.^` for elementwise power operations across vectors, row vectors, and matrices

All available since 2.30.

## Dot Products and Specialized Products

### Standard Products
- `dot_product(complex_vector, complex_vector|complex_row_vector)` -> `complex`
- `dot_product(complex_row_vector, complex_vector|complex_row_vector)` -> `complex`

### Column/Row Operations
- `columns_dot_product(complex_vector|complex_row_vector|complex_matrix, ...)` -> `complex_row_vector`
- `rows_dot_product(complex_vector|complex_row_vector|complex_matrix, ...)` -> `complex_vector`
- `dot_self(complex_vector|complex_row_vector)` -> `complex`
- `columns_dot_self(complex_vector|complex_row_vector|complex_matrix)` -> `complex_row_vector`
- `rows_dot_self(complex_vector|complex_row_vector|complex_matrix)` -> `complex_vector`

### Specialized Products
- `diag_pre_multiply(complex_vector|complex_row_vector, complex_matrix)` -> `complex_matrix`
- `diag_post_multiply(complex_matrix, complex_vector|complex_row_vector)` -> `complex_matrix`

All available since 2.30.

## Reductions

- `sum(complex_vector|complex_row_vector|complex_matrix)` -> `complex`
- `prod(complex_vector|complex_row_vector|complex_matrix)` -> `complex`

Returns 0 for empty sum; 1 for empty product.

## Vectorized Accessor Functions

### Type Demotion
Functions return the same shape object demoted to `real`:
- `get_real(T)` - extracts real components
- `get_imag(T)` - extracts imaginary components

Where `T` can be `complex`, `complex_vector`, `complex_row_vector`, `complex_matrix`, or arrays thereof.

Example: `get_real([3+4i, 5+6i]')` yields `[3, 5]'`

All available since 2.30.

## Broadcast Functions

- `rep_vector(complex, int)` -> `complex_vector`
- `rep_row_vector(complex, int)` -> `complex_row_vector`
- `rep_matrix(complex, int, int)` -> `complex_matrix`
- `rep_matrix(complex_vector, int)` - replicates vector horizontally
- `rep_matrix(complex_row_vector, int)` - replicates row vector vertically
- `symmetrize_from_lower_tri(complex_matrix)` -> `complex_matrix`

All available since 2.30.

## Diagonal Functions

- `add_diag(complex_matrix, complex_row_vector|complex_vector|complex)` -> `complex_matrix`
- `diagonal(complex_matrix)` -> `complex_vector`
- `diag_matrix(complex_vector)` -> `complex_matrix`

All available since 2.30.

## Slicing and Blocking

### Columns/Rows
- `col(complex_matrix, int)` -> `complex_vector`
- `row(complex_matrix, int)` -> `complex_row_vector`

### Block Operations
- `block(complex_matrix, int, int, int, int)` -> `complex_matrix`
- `sub_col(complex_matrix, int, int, int)` -> `complex_vector`
- `sub_row(complex_matrix, int, int, int)` -> `complex_row_vector`

### Vector Slicing
- `head(complex_vector|complex_row_vector, int)` - first n elements
- `tail(complex_vector|complex_row_vector, int)` - last n elements
- `segment(complex_vector|complex_row_vector, int, int)` - n elements starting at position i

All available since 2.30.

## Concatenation

### Horizontal
- `append_col(complex_matrix, complex_matrix|complex_vector)`
- `append_col(complex_vector, complex_matrix|complex_vector)`
- `append_col(complex_row_vector, complex_row_vector|complex)` - appends to row vector

### Vertical
- `append_row(complex_matrix, complex_matrix|complex_row_vector)`
- `append_row(complex_row_vector, complex_matrix|complex_row_vector)`
- `append_row(complex_vector, complex_vector|complex)` - concatenates vectors

All available since 2.30.

## Special Matrix Functions

### Fast Fourier Transforms

FFT functions use scaling where `fft(inv_fft(u)) == u` and `inv_fft(fft(v)) == v`.

- `fft(complex_vector)` -> `complex_vector` - discrete Fourier transform
- `inv_fft(complex_vector)` -> `complex_vector` - inverse FFT with 1/N scaling
- `fft2(complex_matrix)` -> `complex_matrix` - 2D FFT (row-wise then column-wise)
- `inv_fft2(complex_matrix)` -> `complex_matrix` - 2D inverse FFT

All available since 2.30.

### Cumulative Sums

- `cumulative_sum(array[] complex)` -> `array[] complex`
- `cumulative_sum(complex_vector)` -> `complex_vector`
- `cumulative_sum(complex_row_vector)` -> `complex_row_vector`

All available since 2.30.

## Linear Algebra Functions

### Matrix Division
- `operator/(complex_row_vector, complex_matrix)` -> `complex_row_vector` (right division)
- `operator/(complex_matrix, complex_matrix)` -> `complex_matrix` (right division)

### Trace
- `trace(complex_matrix)` -> `complex` (0 if empty)

Available since 2.30.

### Eigendecomposition

- `eigenvalues(complex_matrix)` -> `complex_vector` (since 2.32)
- `eigenvectors(complex_matrix)` -> `complex_matrix` (since 2.32)
- `eigendecompose(complex_matrix)` -> `tuple(complex_matrix, complex_vector)` (since 2.33)
- `eigenvalues_sym(complex_matrix)` -> `complex_vector` (since 2.30)
- `eigenvectors_sym(complex_matrix)` -> `complex_matrix` (since 2.30)
- `eigendecompose_sym(complex_matrix)` -> `tuple(complex_matrix, complex_vector)` (since 2.33)

Note: "Eigenvectors are identified only up to sign change. Multiplying an eigenvector by -1 results in an eigenvector."

### Singular Value Decomposition

For matrix A = U D V^T where U and V are thin matrices:

- `singular_values(complex_matrix)` -> `vector` (descending order)
- `svd_U(complex_matrix)` -> `complex_matrix`
- `svd_V(complex_matrix)` -> `complex_matrix`
- `svd(complex_matrix)` -> `tuple(complex_matrix, vector, complex_matrix)` (since 2.33)

All available since 2.30 except where noted.

### Complex Schur Decomposition

Produces unitary matrix U and upper-triangular Schur form T such that A = U * T * U^(-1), where U^(-1) = U*.

- `complex_schur_decompose_t(matrix|complex_matrix)` -> `complex_matrix` (since 2.31)
- `complex_schur_decompose_u(matrix|complex_matrix)` -> `complex_matrix` (since 2.31)
- `complex_schur_decompose(matrix|complex_matrix)` -> `tuple(complex_matrix, complex_matrix)` (since 2.33)

## Reverse Functions

- `reverse(complex_vector)` -> `complex_vector`
- `reverse(complex_row_vector)` -> `complex_row_vector`

Available since 2.30.

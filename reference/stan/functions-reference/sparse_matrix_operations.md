# Sparse Matrix Operations

## Overview

Stan implements sparse matrix operations for matrices with many zero elements. According to the documentation, "it is more efficient to use specialized representations to save memory and speed up matrix arithmetic." The implementation provides substantial memory savings, though speed improvements typically require "90% or even greater sparsity."

## Compressed Row Storage (CSR)

Sparse matrices use compressed row storage, representing a matrix through three components:

- **w(A)**: A vector of non-zero values read row-by-row
- **v(A)**: An integer array of column indices for each value
- **u(A)**: An integer array indicating where each row's values start in w(A)

For example, the matrix shown uses this structure: w = [19, 27, 52, 81, 95, 33], v = [1, 2, 4, 1, 3, 4], u = [1, 3, 3, 4, 7].

Memory usage is approximately "12 K + M bytes plus a small constant overhead," where K represents non-zero entries.

## Conversion Functions

### Dense to Sparse

- `vector csr_extract_w(matrix a)` - Returns non-zero values
- `array[] int csr_extract_v(matrix a)` - Returns column indices
- `array[] int csr_extract_u(matrix a)` - Returns row starting indices
- `tuple(vector, array[] int, array[] int) csr_extract(matrix a)` - Returns all three components (Available since 2.33)

### Sparse to Dense

- `matrix csr_to_dense_matrix(int m, int n, vector w, array[] int v, array[] int u)` - Converts CSR representation to dense matrix format

## Sparse Matrix Arithmetic

### Sparse Matrix Multiplication

`vector csr_matrix_times_vector(int m, int n, vector w, array[] int v, array[] int u, vector b)`

Multiplies an m x n sparse matrix by a dense vector b. Row vector multiplication requires transposition: b*A = (A^T*b^T)^T.

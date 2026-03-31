# Mixed Operations

These functions perform conversions between Stan containers: matrix, vector, row vector, and arrays.

## to_matrix Functions

`matrix to_matrix(matrix m)` — Return the matrix `m` itself. (Available since 2.3)

`complex_matrix to_matrix(complex_matrix m)` — Return the matrix `m` itself. (Available since 2.30)

`matrix to_matrix(vector v)` — Convert column vector `v` to a size(v) by 1 matrix. (Available since 2.3)

`complex_matrix to_matrix(complex_vector v)` — Convert column vector `v` to a size(v) by 1 matrix. (Available since 2.30)

`matrix to_matrix(row_vector v)` — Convert row vector `v` to a 1 by size(v) matrix. (Available since 2.3)

`complex_matrix to_matrix(complex_row_vector v)` — Convert row vector `v` to a 1 by size(v) matrix. (Available since 2.30)

`matrix to_matrix(matrix M, int m, int n)` — Transform a matrix to dimensions m rows and n columns using column-major order. (Available since 2.15)

`complex_matrix to_matrix(complex_matrix M, int m, int n)` — Transform a complex matrix to dimensions m rows and n columns using column-major order. (Available since 2.30)

`matrix to_matrix(vector v, int m, int n)` — Transform a vector to a matrix with m rows and n columns using column-major order. (Available since 2.15)

`complex_matrix to_matrix(complex_vector v, int m, int n)` — Transform a complex vector to a matrix with m rows and n columns using column-major order. (Available since 2.30)

`matrix to_matrix(row_vector v, int m, int n)` — Transform a row_vector to a matrix with m rows and n columns using column-major order. (Available since 2.15)

`complex_matrix to_matrix(complex_row_vector v, int m, int n)` — Transform a complex row vector to a matrix with m rows and n columns using column-major order. (Available since 2.30)

`matrix to_matrix(matrix A, int m, int n, int col_major)` — Transform a matrix to dimensions m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.15)

`complex_matrix to_matrix(complex_matrix A, int m, int n, int col_major)` — Transform a complex matrix to dimensions m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.30)

`matrix to_matrix(vector v, int m, int n, int col_major)` — Transform a vector to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.15)

`complex_matrix to_matrix(complex_vector v, int m, int n, int col_major)` — Transform a complex vector to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.30)

`matrix to_matrix(row_vector v, int m, int n, int col_major)` — Transform a row vector to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.15)

`complex_matrix to_matrix(complex_row_vector v, int m, int n, int col_major)` — Transform a complex row vector to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.30)

`matrix to_matrix(array[] real a, int m, int n)` — Transform a one-dimensional real array to a matrix with m rows and n columns using column-major order. (Available since 2.15)

`matrix to_matrix(array[] int a, int m, int n)` — Transform a one-dimensional integer array to a matrix with m rows and n columns using column-major order. (Available since 2.15)

`complex_matrix to_matrix(array[] complex a, int m, int n)` — Transform a one-dimensional complex array to a matrix with m rows and n columns using column-major order. (Available since 2.30)

`matrix to_matrix(array[] real a, int m, int n, int col_major)` — Transform a one-dimensional real array to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.15)

`matrix to_matrix(array[] int a, int m, int n, int col_major)` — Transform a one-dimensional integer array to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.15)

`complex_matrix to_matrix(array[] complex a, int m, int n, int col_major)` — Transform a one-dimensional complex array to a matrix with m rows and n columns. When `col_major` equals 0, use row-major order; otherwise use column-major. (Available since 2.30)

`matrix to_matrix(array[] row_vector vs)` — Transform a one-dimensional array of row vectors to a matrix where array size becomes row count and row vector length becomes column count. (Available since 2.28)

`complex_matrix to_matrix(array[] complex_row_vector vs)` — Transform a one-dimensional array of complex row vectors to a matrix where array size becomes row count and row vector length becomes column count. (Available since 2.30)

`matrix to_matrix(array[,] real a)` — Transform a two-dimensional real array to a matrix with identical dimensions and indexing order. (Available since 2.3)

`matrix to_matrix(array[,] int a)` — Transform a two-dimensional integer array to a matrix with identical dimensions and indexing order. Zero dimensions result in a 0x0 matrix. (Available since 2.3)

`complex_matrix to_matrix(array[,] complex a)` — Transform a two-dimensional complex array to a matrix with identical dimensions and indexing order. (Available since 2.30)

## to_vector Functions

`vector to_vector(matrix m)` — Transform a matrix to a column vector in column-major order. (Available since 2.0)

`complex_vector to_vector(complex_matrix m)` — Transform a complex matrix to a column vector in column-major order. (Available since 2.30)

`vector to_vector(vector v)` — Return the column vector `v` itself. (Available since 2.3)

`complex_vector to_vector(complex_vector v)` — Return the complex column vector `v` itself. (Available since 2.30)

`vector to_vector(row_vector v)` — Transform a row vector to a column vector. (Available since 2.3)

`complex_vector to_vector(complex_row_vector v)` — Transform a complex row vector to a column vector. (Available since 2.30)

`vector to_vector(array[] real a)` — Transform a one-dimensional real array to a column vector. (Available since 2.3)

`vector to_vector(array[] int a)` — Transform a one-dimensional integer array to a column vector. (Available since 2.3)

`complex_vector to_vector(array[] complex a)` — Transform a one-dimensional complex array to a column vector. (Available since 2.30)

## to_row_vector Functions

`row_vector to_row_vector(matrix m)` — Transform a matrix to a row vector in column-major order. (Available since 2.3)

`complex_row_vector to_row_vector(complex_matrix m)` — Transform a complex matrix to a row vector in column-major order. (Available since 2.30)

`row_vector to_row_vector(vector v)` — Transform a column vector to a row vector. (Available since 2.3)

`complex_row_vector to_row_vector(complex_vector v)` — Transform a complex column vector to a row vector. (Available since 2.30)

`row_vector to_row_vector(row_vector v)` — Return the row vector `v` itself. (Available since 2.3)

`complex_row_vector to_row_vector(complex_row_vector v)` — Return the complex row vector `v` itself. (Available since 2.30)

`row_vector to_row_vector(array[] real a)` — Transform a one-dimensional real array to a row vector. (Available since 2.3)

`row_vector to_row_vector(array[] int a)` — Transform a one-dimensional integer array to a row vector. (Available since 2.3)

`complex_row_vector to_row_vector(array[] complex a)` — Transform a one-dimensional complex array to a row vector. (Available since 2.30)

## to_array_2d Functions

`array[,] real to_array_2d(matrix m)` — Transform a matrix to a two-dimensional real array with identical dimensions and indexing order. (Available since 2.3)

`array[,] complex to_array_2d(complex_matrix m)` — Transform a complex matrix to a two-dimensional complex array with identical dimensions and indexing order. (Available since 2.30)

## to_array_1d Functions

`array[] real to_array_1d(vector v)` — Transform a column vector to a one-dimensional real array. (Available since 2.3)

`array[] complex to_array_1d(complex_vector v)` — Transform a complex column vector to a one-dimensional complex array. (Available since 2.30)

`array[] real to_array_1d(row_vector v)` — Transform a row vector to a one-dimensional real array. (Available since 2.3)

`array[] complex to_array_1d(complex_row_vector v)` — Transform a complex row vector to a one-dimensional complex array. (Available since 2.30)

`array[] real to_array_1d(matrix m)` — Transform a matrix to a one-dimensional real array in column-major order. (Available since 2.3)

`array[] real to_array_1d(complex_matrix m)` — Transform a complex matrix to a one-dimensional real array in column-major order. (Available since 2.30)

`array[] real to_array_1d(array[...] real a)` — Transform any-dimensional real array (up to 10 dimensions) to a one-dimensional real array in row-major order. (Available since 2.3)

`array[] int to_array_1d(array[...] int a)` — Transform any-dimensional integer array (up to 10 dimensions) to a one-dimensional integer array in row-major order. (Available since 2.3)

`array[] complex to_array_1d(array[...] complex a)` — Transform any-dimensional complex array (up to 10 dimensions) to a one-dimensional complex array in row-major order. (Available since 2.30)

# Matrices, Vectors, Arrays, and Tuples

## Overview

Stan provides multiple container types for organizing data: matrices, vectors, row vectors, arrays, and tuples. Each has distinct characteristics affecting efficiency and functionality.

## Basic Container Types

Stan includes three scalar types (`int`, `real`, `complex`) and three linear algebra types (`vector`, `row_vector`, `matrix`). Arrays can have any dimensionality and contain any single type of element.

### One-Dimensional Containers

Three ways exist to declare a one-dimensional container of size N:

```stan
array[N] real a;
vector[N] a;
row_vector[N] a;
```

These distinctions matter because matrix types are required for linear algebra operations. No automatic promotion occurs between arrays and vectors since the target (row or column vector) would be ambiguous.

### Two-Dimensional Containers

Four methods exist to declare a container of size M × N:

```stan
array[M, N] real b;          // b[m] : array[] real     (efficient)
array[M] vector[N] b;        // b[m] : vector     (efficient)
array[M] row_vector[N] b;    // b[m] : row_vector (efficient)
matrix[M, N] b;              // b[m] : row_vector (inefficient)
```

The key differences involve efficiency and the type returned when indexing. Only the fourth declaration permits matrix operations, while the third allows efficient row vector iteration.

## Tuple Types

Tuples represent sequences of heterogeneous types, addressing limitations of arrays and vectors that require uniform element types.

### Tuple Declaration and Construction

Tuples use the `tuple` keyword with type declarations in parentheses:

```stan
tuple(int, vector[3]) ny = (5, [3, 2.9, 1.8]');
```

Elements are accessed by position starting from 1:

```stan
int n = ny.1;
vector[3] y = ny.2;
```

Elements can be assigned individually:

```stan
tuple(int, vector[3], complex) abc;
abc.1 = 5;
abc.2[1] = 3;
abc.2[2] = 2.9;
abc.2[3] = 1.4798;
abc.3 = 2 + 1.9j;
```

Result values function as lvalues, permitting further indexing like `abc.2[1]`.

### Tuple Efficiency Considerations

Tuples are passed to functions by constant reference (pointer only), but construction copies all element data. This example illustrates the copying behavior:

```stan
int a = 5;
matrix[10, 100] b = ...;
tuple(int, matrix[10, 100]) ab = (a, b);  // COPIES b
b[1,1] = 10.3;  // does NOT change ab
```

### Tuple Applications

**Structure encapsulation**: Tuples group heterogeneous items for passing as single arguments:

```stan
array[N] tuple(int, real, vector[5])  // array of structures
tuple(array[N] int, array[N] real, array[N] vector[5])  // structure of arrays
```

**Function return values**: Functions can return multiple values of different types. Example with QR decomposition:

```stan
matrix[M, N] A = ...;
tuple(matrix[M, M], matrix[M, N]) QR = qr(A);
// QR.1 is Q, QR.2 is R
```

Previously required two separate function calls.

## Fixed Sizes and Indexing

All matrix, vector, and array variables have fixed sizes at declaration. While declarations inside loops may vary, each creates a fixed-size object. Out-of-bounds indexing triggers rejection errors halting computation on the current log density and gradient evaluation.

## Data Type and Indexing Efficiency

Matrix and linear algebra operations use Eigen C++ library implementations. Vectors and matrices as basic types eliminate conversion overhead. Arrays use C++ `std::vector` class, enabling efficient return-by-reference indexing.

### Matrices vs. Two-Dimensional Arrays

Several efficiency differences exist:

**Memory usage**: Matrices consume less memory than two-dimensional arrays since they store only data and dimensions, not sequences of arrays.

**Storage order**: Matrices use column-major order with guaranteed contiguous memory. This matters for CPU cache efficiency—memory fetching costs far exceed arithmetic operations. Arrays guarantee contiguous primitive-type values only.

**Traversal order**: Matrices should traverse in column-major order:

```stan
matrix[M, N] a;
for (n in 1:N) {
  for (m in 1:M) {
    // ... do something with a[m, n] ...
  }
}
```

Arrays should traverse in row-major order (last index fastest):

```stan
array[M, N] real a;
for (m in 1:M) {
  for (n in 1:N) {
    // ... do something with a[m, n] ...
  }
}
```

**Optimal traversal for array of matrices**:

```stan
array[I, J] matrix[M, N] b;
for (i in 1:I) {
  for (j in 1:J) {
    for (n in 1:N) {
      for (m in 1:M) {
        // ... do something with b[i, j, m, n] ...
      }
    }
  }
}
```

**Row extraction efficiency**: Extracting `a[m]` from a matrix is inefficient. Use array of row vectors instead:

```stan
array[M] row_vector[N] b;  // EFFICIENT
for (m in 1:M) {
   // ... do something with row vector b[m] ...
}
```

versus:

```stan
matrix[M, N] b;  // INEFFICIENT
for (m in 1:M) {
   // ... do something with row vector b[m] ...
}
```

**Matrix algebra efficiency**: Pure matrix operations are fastest:

```stan
matrix[N, K] x;
vector[K] beta;
vector[N] y_hat;
y_hat = x * beta;  // EFFICIENT
```

compared to:

```stan
array[N] row_vector[K] x;
vector[K] beta;
vector[N] y_hat;
for (n in 1:N) {
  y_hat[n] = x[n] * beta;  // LESS EFFICIENT
}
```

### Row Vectors vs. One-Dimensional Arrays

For container use alone, no significant practical differences exist between vectors, row vectors, and one-dimensional arrays. Both Eigen::Vector specializations and std::vector are similarly implemented for `double` values (Stan's `real` type). Only arrays can store integer values.

## Memory Locality

CPU memory arrives in cache blocks. Fetching from main memory is dramatically slower than arithmetic operations. Container operation speed depends on respecting memory locality and sequential access to nearby elements.

### Matrix Storage

Matrices store internally in column-major order. An M × N matrix stores elements as:
(1,1), (2,1), …, (M,1), (1,2), …, (M,2), …, (1,N), …, (M,N)

This makes column-by-column loops most efficient:

```stan
matrix[M, N] a;
for (n in 1:N) {
  for (m in 1:M) {
     // ... do something with a[m, n] ...
  }
}
```

Row extraction requires striding and copying. Use arrays of row vectors for row-sequential access:

```stan
array[M] row_vector[N] a;
for (m in 1:M) {
  // ... do something with row vector a[m] ...
}
```

### Array Storage

Arrays store following their data structure. Two-dimensional arrays use row-major order, making row extraction efficient:

```stan
array[M, N] real a;
for (m in 1:M) {
  // ... do something with a[m] ...
}
```

However, entries `a[m]` in two-dimensional arrays aren't necessarily adjacent in memory, providing no guaranteed memory locality across rows during full iteration.

## Type Conversion

Stan provides no automatic conversion between matrices, vectors, and arrays. Conversion functions exist for transforming matrices to vectors, multi-dimensional arrays to one-dimensional arrays, and vectors to arrays. See the functions reference manual section on mixed matrix and array operations and the multi-indexing chapter for reshaping operations.

## Aliasing in Stan Containers

Stan evaluates all expressions before assignment, eliminating aliasing dangers in array, vector, and matrix operations.

Example contrast between loop assignment and sliced assignment:

```stan
transformed data {
  vector[4] x = [ 1, 2, 3, 4 ]';
  vector[4] u = [ 1, 2, 3, 4 ]';

  for (t in 2:4) {
    u[t] = u[t - 1] * 3;
  }

  x[2:4] = x[1:3] * 3;

  print("u = ", u);
  print("x = ", x);
}
```

Output:

```
u = [1, 3, 9, 27]
x = [1, 3, 6, 9]
```

Loop assignment updates values before using them for subsequent values. Sliced assignment evaluates the entire right-hand side before assigning to the left-hand side.

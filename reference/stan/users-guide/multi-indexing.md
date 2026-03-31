# Multiple Indexing and Range Indexing in Stan

## Overview

Stan supports advanced indexing techniques that enable vectorized operations on containers like arrays, vectors, and matrices. These features allow for more efficient and readable code compared to explicit loops.

## Multiple Indexing

### Basic Concept

Multiple indexing uses an array of integers to select multiple elements simultaneously. As the documentation explains: "The multiple indexed expression `c[idxs]` is defined by extracting elements at each position specified in the index array."

**Example:**
```stan
array[3] int c;  // c == (5, 9, 7)
array[4] int idxs;  // idxs == (3, 3, 1, 2)
array[4] int d;
d = c[idxs];  // result: d == (7, 7, 5, 9)
```

### Multi-dimensional Arrays

Multiple indexing works with multi-dimensional structures. Single indices reduce dimensionality, while multiple indices maintain it.

**Two-dimensional example:**
```stan
array[2, 3] int c;
array[4] int idxs;
array[4, 3] int d;
d = c[idxs];
```

## Range Indexing (Slicing)

### Bounded Ranges

The notation `c[3:6]` extracts elements from index 3 through 6. This is semantically equivalent to providing multiple indexes but more efficient.

**Example:**
```stan
array[7] int c;
array[4] int d;
d = c[3:6];  // equivalent to (c[3], c[4], c[5], c[6])
```

### Open-ended Ranges

- `c[3:]` is shorthand for `c[3:size(c)]`
- `c[:5]` is shorthand for `c[1:5]`
- `c[:]` or `c[]` covers the entire array

### Specialized Slicing Functions

Stan provides helper functions:
- `head(a, N)`: first N elements
- `tail(a, N)`: last N elements
- `segment(a, pos, length)`: contiguous segment starting at position

**Example:**
```stan
array[15] a;
array[3] b = segment(a, 5, 3);  // elements at positions 5, 6, 7
```

## Assignment with Multiple Indexing

Multiple indexing works on the left-hand side of assignments. The key principle: "The right-hand side expression is evaluated to a fresh copy before assignment."

**Example:**
```stan
array[3] int a;  // a == (1, 2, 3)
array[2] int c;  // c == (5, 9)
array[2] int idxs;  // idxs = (3, 2)
a[idxs] = c;  // result: a == (1, 9, 5)
```

This sets `a[3] = c[1]` and `a[2] = c[2]`.

### Aliasing Behavior

When the same data appears on both sides, Stan creates a copy first to avoid unintended modifications.

```stan
array[3] int a;  // a == (5, 6, 7)
a[2:3] = a[1:2];  // result: a == (5, 5, 6)
```

## Vectors and Matrices

### Type Inference Rules

"Single indexes reduce dimensionality, while multiple indexes preserve dimensions."

**Vector examples:**
```stan
vector[5] v;
vector[3] u = v[2:4];  // extracts elements 2, 3, 4
```

**Matrix examples:**
```stan
matrix[5, 7] m;
row_vector[3] rv = m[4, 3:5];  // row 4, columns 3-5
vector[4] v = m[2:5, 3];  // rows 2-5, column 3
matrix[3, 4] m2 = m[1:3, 2:5];  // submatrix
```

### Matrix Block Operations

Specialized functions provide intuitive matrix slicing:
- `block(a, row_start, col_start, num_rows, num_cols)`: rectangular block
- `sub_col(a, col, row_start, num_rows)`: column segment
- `sub_row(a, row, col_start, num_cols)`: row segment

**Example:**
```stan
matrix[20, 20] a;
matrix[3, 2] b = block(a, 5, 9, 3, 2);  // submatrix starting at [5,9]
```

## Practical Application: Sparse Parameter Matrices

Multiple indexing enables efficient handling of structured matrices with known zeros:

```stan
transformed data {
  array[7, 2] int<lower=1, upper=3> idxs = {
    {1, 1}, {2, 1}, {2, 2}, {2, 3},
    {3, 1}, {3, 2}, {3, 3}
  };
}

parameters {
  vector[7] A_raw;
}

model {
  matrix[3, 3] A;
  for (i in 1:7) {
    A[idxs[i, 1], idxs[i, 2]] = A_raw[i];
  }
  A[1, 2] = 0;
  A[1, 3] = 0;
}
```

This pattern efficiently represents sparse or partially-known matrices by storing only non-zero or unknown elements.

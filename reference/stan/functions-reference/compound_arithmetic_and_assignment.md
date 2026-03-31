# Compound Arithmetic and Assignment

## Overview

Compound arithmetic and assignment statements combine an arithmetic operation with assignment, replacing statements like `x = x op y;` with the more compact form `x op= y;`. For example, `x = x + 1;` can be written as `x += 1;`.

These operations work with scalar types (`int`, `real`, `complex`), real matrix types (`vector`, `row_vector`, `matrix`), and complex matrix types (`complex_vector`, `complex_row_vector`, `complex_matrix`).

## Operators

### Compound Addition and Assignment

**`operator+=`**`(T x, U y)`

This operation is equivalent to `x = x + y`. It functions wherever the corresponding addition would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

### Compound Subtraction and Assignment

**`operator-=`**`(T x, U y)`

This operation is equivalent to `x = x - y`. It functions wherever the corresponding subtraction would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

### Compound Multiplication and Assignment

**`operator*=`**`(T x, U y)`

This operation is equivalent to `x = x * y`. It functions wherever the corresponding multiplication would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

### Compound Division and Assignment

**`operator/=`**`(T x, U y)`

This operation is equivalent to `x = x / y`. It functions wherever the corresponding division would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

### Compound Elementwise Multiplication and Assignment

**`operator.*=`**`(T x, U y)`

This operation is equivalent to `x = x .* y`. It functions wherever the corresponding elementwise multiplication would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

### Compound Elementwise Division and Assignment

**`operator./=`**`(T x, U y)`

This operation is equivalent to `x = x ./ y`. It functions wherever the corresponding elementwise division would be properly formed.

Available since version 2.17; complex signatures added in 2.30.

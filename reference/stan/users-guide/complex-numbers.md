# Complex Numbers in Stan

## Overview

Stan provides comprehensive support for complex-valued computations across scalars, vectors, matrices, and arrays. This enables sophisticated mathematical modeling involving complex quantities.

## Core Concepts

### Construction and Access

Complex numbers are created using imaginary literals or the `to_complex()` function:

```stan
complex z = -1.1 + 2.3i;
real x = get_real(z);
real y = get_imag(z);
```

The `to_complex()` function constructs complex values from arbitrary real variables, particularly useful when working with parameters or computed quantities.

### Type Promotion

Integer- or real-valued expressions may be assigned to complex numbers, with the corresponding imaginary component set to zero. This automatic conversion simplifies code where mixed numeric types appear.

## Advanced Structures

### Complex Arrays and Collections

Complex arrays follow standard syntax conventions and support curly bracket initialization. Elements can be assigned values with automatic promotion from real or integer types to complex.

### Complex Functions

Stan implements all of the standard complex functions, including natural logarithm `log(z)`, natural exponentiation `exp(z)`, and powers `pow(z1, z2)`, as well as all of the trig and hyperbolic trigonometric functions and their inverses.

### Complex Matrices and Vectors

Three specialized types exist: `complex_vector`, `complex_row_vector`, and `complex_matrix`. These support all of the standard arithmetic operations including negation, addition, subtraction, and multiplication. They also support transposition.

## Practical Applications

### Random Variables

Complex distributions leverage bivariate normal models for the real and imaginary components via multivariate normal specifications.

### Linear Regression

Complex regression follows familiar patterns with either independent or correlated error structures for real and imaginary components, depending on modeling requirements.

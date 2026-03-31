# Complex-Valued Basic Functions in Stan

## Overview

This documentation describes built-in functions for complex number operations in Stan version 2.28+, including arithmetic operators, constructors, accessors, and specialized functions.

## Complex Assignment and Promotion

Values can be promoted from integer or real to complex types, with imaginary components defaulting to zero:

```stan
int n = 5;
real x = n;           // x = 5.0
complex z1 = n;       // z1 = 5.0 + 0.0i
complex z2 = x;       // z2 = 5.0 + 0.0i
```

### Function Argument Promotion

"Function arguments of type `int` or `real` may be promoted to type `complex`. The complex version of functions in this chapter are only used if one of the arguments is complex."

## Constructors

**`to_complex()`** - Returns 0.0 + 0.0i

**`to_complex(real re)`** - Returns complex with real part `re` and imaginary part 0.0

**`to_complex(real re, real im)`** - Returns complex with real part `re` and imaginary part `im`

**`to_complex(T1 re, T2 im)`** - Vectorized version accepting containers of equal size or a container and scalar

## Accessors

**`get_real(complex z)`** - Extracts the real component

**`get_imag(complex z)`** - Extracts the imaginary component

## Arithmetic Operators

### Unary Operators

**`operator+(complex z)`** - Returns `z` unchanged

**`operator-(complex z)`** - Returns negation: for z = x + yi, result is -x - yi

**`operator-(T x)`** - Vectorized negation for complex arrays

### Binary Operators

**`operator+(complex x, complex y)`** - Addition

**`operator-(complex x, complex y)`** - Subtraction

**`operator*(complex x, complex y)`** - Multiplication

**`operator/(complex x, complex y)`** - Division

**`operator^(complex x, complex y)`** - Power: computed as exp(y log(x))

## Comparison Operators

**`operator==(complex x, complex y)`** - Returns 1 if both real and imaginary components equal, else 0

**`operator!=(complex x, complex y)`** - Returns 1 if values unequal, else 0

**Warning:** "As with real values, it is usually a mistake to compare complex numbers for equality because their parts are implemented using floating-point arithmetic, which suffers from precision errors."

## Assignment Operators

**`operator=(complex x, complex y)`** - Assigns y to x

**`operator+=(complex x, complex y)`** - Equivalent to x = x + y

**`operator-=(complex x, complex y)`** - Equivalent to x = x - y

**`operator*=(complex x, complex y)`** - Equivalent to x = x * y

**`operator/=(complex x, complex y)`** - Equivalent to x = x / y

## Special Functions

**`abs(complex z)`** - Magnitude: sqrt(x^2 + y^2). Returns real, works elementwise over containers.

**`arg(complex z)`** - Phase angle in radians: atan2(y, x)

**`norm(complex z)`** - Euclidean norm (absolute value squared): x^2 + y^2

**`conj(complex z)`** - Complex conjugate: x - yi

**`conj(Z z)`** - Vectorized conjugate for complex arrays

**`proj(complex z)`** - Riemann sphere projection. Finite values unchanged; infinite values map to sign(y)i

**`polar(real r, real theta)`** - Constructs complex from magnitude r and phase angle theta

## Exponential and Power Functions

**`exp(complex z)`** - Complex exponential: exp(x)(cos(y) + i sin(y))

**`log(complex z)`** - Complex natural logarithm: log(r) + theta*i for polar(r, theta)

**`log10(complex z)`** - Complex base-10 logarithm: log(z) / log(10)

**`pow(complex x, complex y)`** - Power function: exp(y log(x))

**`pow(T1 x, T2 y)`** - Vectorized power function

**`sqrt(complex x)`** - Complex square root with branch cut along negative real axis

## Trigonometric Functions

**`cos(complex z)`** - Complex cosine: cosh(zi) = (exp(zi) + exp(-zi)) / 2

**`sin(complex z)`** - Complex sine: (exp(zi) - exp(-zi)) / (2i)

**`tan(complex z)`** - Complex tangent

**`acos(complex z)`** - Complex arc cosine

**`asin(complex z)`** - Complex arc sine

**`atan(complex z)`** - Complex arc tangent

## Hyperbolic Trigonometric Functions

**`cosh(complex z)`** - Hyperbolic cosine: (exp(z) + exp(-z)) / 2

**`sinh(complex z)`** - Hyperbolic sine: (exp(z) - exp(-z)) / 2

**`tanh(complex z)`** - Hyperbolic tangent: sinh(z) / cosh(z)

**`acosh(complex z)`** - Arc hyperbolic cosine: log(z + sqrt((z+1)(z-1)))

**`asinh(complex z)`** - Arc hyperbolic sine: log(z + sqrt(1 + z^2))

**`atanh(complex z)`** - Arc hyperbolic tangent: (log(1+z) - log(1-z)) / 2

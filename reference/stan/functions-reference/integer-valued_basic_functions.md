# Integer-Valued Basic Functions

## Overview
This section documents Stan's built-in functions that accept various argument types and return integer values.

## Integer-Valued Arithmetic Operators

### Binary Infix Operators

**`int operator+(int x, int y)`**
"The sum of the addends x and y" with formula: `operator+(x,y) = (x + y)`
Available since 2.0

**`int operator-(int x, int y)`**
"The difference between the minuend x and subtrahend y" with formula: `operator-(x,y) = (x - y)`
Available since 2.0

**`int operator*(int x, int y)`**
"The product of the factors x and y" with formula: `operator*(x,y) = (x * y)`
Available since 2.0

**`int operator/(int x, int y)`**
"The integer quotient of the dividend x and divisor y" (deprecated; use `operator%/%` instead)
Available since 2.0, deprecated in 2.24

**`int operator%/%(int x, int y)`**
"The integer quotient of the dividend x and divisor y" with conditional formula based on sign
Available since 2.24

**`int operator%(int x, int y)`**
"x modulo y, which is the positive remainder after dividing x by y"
Available since 2.13

### Unary Prefix Operators

**`int operator-(int x)`**
"The negation of the subtrahend x" with formula: `operator-(x) = -x`
Available since 2.0

**`T operator-(T x)`**
Vectorized negation for arrays of integers
Available since 2.31

**`int operator+(int x)`**
"This is a no-op" with formula: `operator+(x) = x`
Available since 2.0

## Absolute Functions

**`T abs(T x)`**
"The absolute value of x. This function works elementwise over containers such as vectors."
Available since 2.0, vectorized in 2.30

**`int int_step(int x)` / `int int_step(real x)`**
"Return the step function of x as an integer" returning 1 if x > 0, otherwise 0
Warning: behavior differs from `step()` at boundary cases
Available since 2.0

## Bound Functions

**`int min(int x, int y)`**
Returns the minimum value with conditional formula
Available since 2.0

**`int max(int x, int y)`**
Returns the maximum value with conditional formula
Available since 2.0

## Size Functions

**`int size(int x)` / `int size(real x)`**
"Return the size of `x` which for scalar-valued `x` is 1"
Available since 2.26

## Casting Functions

**`int to_int(data real x)`**
"Return the value `x` truncated to an integer" (data-only qualifier required)
Available since 2.31

**`I to_int(data T x)`**
Vectorized version accepting nested arrays of reals
Available since 2.31

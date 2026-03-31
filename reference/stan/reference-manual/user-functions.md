# User-Defined Functions in Stan

## Overview

Stan permits developers to create custom functions using a simplified C/C++-style syntax. These functions must be declared in a dedicated `functions` block before other program sections.

## Function Definition Structure

Functions appear within a `functions { }` block:

```
functions {
   // function declarations and definitions
}
data {
  // ...
}
```

Forward declarations are permitted but optional.

## Naming and Overloading

Function names follow standard variable naming conventions. Multiple functions may share the same name if their argument type sequences differ—this capability is called **function overloading**.

Example of overloading:
```
real add_up(real a, real b) { return a + b; }
real add_up(real a, real b, real c) { return a + b + c; }
int add_up(int a, int b) { return a + b; }
```

However, functions cannot have identical names if they differ only in return type.

## Function Calling

All arguments are mandatory; default values are unsupported.

### Non-void Functions

Functions returning non-void types operate as expressions, similar to built-in functions.

### Void Functions

Functions declared with `void` return types function as statements, useful for side effects like incrementing log probability or printing.

### Overload Resolution

When multiple overloaded functions match a call, Stan requires a unique signature minimizing type promotions. Ambiguous calls produce compile-time errors.

### Type Promotion

Arguments may be promoted following assignment rules: `int` to `real`, `real` to `complex`, and `int` to `complex`. Container promotions also work (e.g., `array of int` to `array of real`).

### Distribution Functions

Functions ending in `_lpdf` or `_lpmf` may serve as probability functions in distribution statements, replacing parameterized distributions on the right side of `~` operators.

### Placement Restrictions

- Functions ending in `_lp` require log probability accumulator access; restricted to transformed parameters and model blocks
- Functions ending in `_jacobian` restricted to transformed parameters block
- Functions ending in `_rng` require random number generator access; allowed in generated quantities, transformed data blocks, and within other `_rng` functions
- Functions ending in `_lpdf` and `_lpmf` usable anywhere; `_lupdf` and `_lupmf` restricted to model block or probability functions

## Argument Types and Qualifiers

Function arguments require base type and dimensionality declarations without constraints.

### Base Types

Valid base types include: `integer`, `real`, `complex`, `vector`, `row_vector`, `matrix`, and `tuple` types.

### Dimensionality

Arrays use bracket notation: `array[] real` (one-dimensional), `array[,] real` (two-dimensional), etc. Matrices and vectors don't require dimension specifications in declarations.

### Data-Only Arguments

The `data` qualifier restricts arguments to data-only expressions:

```
real foo(data real x) {
  return x^2;
}
```

## Function Bodies

Function bodies contain statements and optional local variable declarations. Recursion (self and mutual) is supported without forward declarations.

### Random Number Generation

Functions using random number generators must end in `_rng`; compilation fails otherwise. These functions operate only in generated quantities, transformed data, or within other `_rng` functions.

### Log Probability Access

Functions containing distribution statements or log probability increments must end in `_lp`. These functions exclusively work in transformed parameters and model blocks.

### Custom Probability Functions

Functions named `_lpdf` or `_lpmf` define custom distributions for use in distribution statements. Automatically generated `_lupdf` and `_lupmf` variants handle unnormalized density behavior differently—the normalized versions force other unnormalized densities to normalize, while unnormalized versions permit additive constants to drop.

Example usage:
```
real foo_lpdf(real y, vector theta) { ... }

z ~ foo(phi);  // equivalent to: target += foo_lupdf(z | phi);
```

## Parameters as Constants

Function parameters maintain constant values throughout execution. Assignment attempts produce compile-time errors.

## Return Values

Non-void functions require return statements with appropriately typed expressions. Void functions may use `return;` without arguments.

### Return Guarantee

Stan enforces syntactic guarantees ensuring non-void functions exit through properly typed return statements or exceptions. The final statement must qualify as a return statement. Conditional statements require default `else` clauses; loops must contain return statements as their final statement.

Example that qualifies:
```
real log_fancy(real x) {
  if (x < 1e-30) {
    return x;
  } else if (x < 1e-14) {
    return x * x;
  } else {
    return log(x);
  }
}
```

## Forward Declarations

Functions may be declared without bodies for use with external C++ implementations:

```
real unit_normal_lpdf(real y);
```

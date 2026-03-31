# Removed Functions

## Overview

This page documents functions that previously existed in Stan but have been replaced or removed.

## `multiply_log` and `binomial_coefficient_log` Functions

**Removed In:** Stan 2.33

**Status:** "Currently two non-conforming functions ending in suffix `_log`"

**Migration Path:**
- Replace `multiply_log(...)` with `lmultiply(...)`
- Replace `binomial_coefficient_log(...)` with `lchoose(...)`

## `get_lp()` Function

**Removed In:** Stan 2.33

**Status:** "The built-in no-argument function `get_lp()` is deprecated"

**Migration Path:** Use the no-argument function `target()` instead

## `fabs` Function

**Removed In:** Stan 2.33

**Status:** "The unary function `fabs` is deprecated"

**Migration Path:** Use `abs` instead. The return type differs for integer overloads but replacement remains safe due to Stan's type promotion rules.

## Exponentiated Quadratic Covariance Functions

**Timeline:** Available since 2.16, deprecated since 2.20, removed in 2.33

**Status:** Replaced by functions in the Gaussian Process Covariance Functions section

**Mathematical Definition:**

The exponentiated quadratic kernel with magnitude alpha and length scale l:

k(x_i, x_j) = alpha^2 exp(-0.5 * rho^-2 * sum_d (x_{i,d} - x_{j,d})^2)

**Removed Signatures:**
- `matrix cov_exp_quad(row_vectors x, real alpha, real rho)`
- `matrix cov_exp_quad(vectors x, real alpha, real rho)`
- `matrix cov_exp_quad(array[] real x, real alpha, real rho)`
- `matrix cov_exp_quad(row_vectors x1, row_vectors x2, real alpha, real rho)`
- `matrix cov_exp_quad(vectors x1, vectors x2, real alpha, real rho)`
- `matrix cov_exp_quad(array[] real x1, array[] real x2, real alpha, real rho)`

## Real Arguments to Logical Operators

**Removed In:** Stan 2.34

**Status:** "A nonzero real number (even NaN) was interpreted as true and zero was interpreted as false"

**Affected Operators:** `operator&&`, `operator||`, `operator!`

**Migration Path:** Use explicit `x != 0` comparison instead

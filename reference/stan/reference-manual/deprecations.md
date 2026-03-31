# Deprecated Features - Stan Reference Manual

## Overview

The Stan Reference Manual documents features that have been deprecated and should no longer be used. According to the page, "Starting with Stan 2.29, minor (syntax-level) deprecations can be removed 3 versions after release."

## Key Deprecations

### 1. `lkj_cov` Distribution

**Status:** Deprecated with removal scheduled for Stan 3.0 or later

**What to do instead:** Replace the `lkj_cov_lpdf` function with a combination of an `lkj_corr` distribution applied to a correlation matrix, plus independent lognormal distributions for scales. The suggested replacement involves:

- Using `Omega ~ lkj_corr(eta)` for the correlation matrix
- Using `sigma ~ lognormal(mu, tau)` for the scales
- Computing the covariance matrix as `Sigma <- quad_form_diag(Omega, sigma)`

The documentation notes that "an even more efficient transform would use Cholesky factors rather than full correlation matrix types."

### 2. Functions Ending in `_lp` in Transformed Parameters Block

**Status:** Deprecated

**Recommendation:** Use `_jacobian` functions with the `jacobian +=` statement instead, which allow conditional enabling of change-of-variable adjustments.

### 3. Deprecated Functions

The page references additional deprecated functions documented in the functions reference section, though specific details aren't provided on this page.

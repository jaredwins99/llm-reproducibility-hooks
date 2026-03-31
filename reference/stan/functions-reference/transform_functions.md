# Variable Transformation Functions - Stan Functions Reference

## Overview

Variable transformation functions implement constraining and unconstraining transforms. For each transform, three functions are provided: a `_constrain` function mapping free variables to constrained space, an `_unconstrain` function mapping constrained space back to free variables, and a `_jacobian` function that also increments the log Jacobian determinant.

## Transforms for Scalars

These functions constrain real values to subsets of the real line or apply affine mappings. Functions are overloaded to work element-wise on containers.

### Lower Bounds

**`lower_bound_constrain(reals y, reals lb)`**
Maps an unconstrained value `y` to a value exceeding lower bound `lb`. Available since 2.37.

**`lower_bound_jacobian(reals y, reals lb)`**
Constrains `y` to exceed `lb` while incrementing the Jacobian accumulator. Available since 2.37.

**`lower_bound_unconstrain(reals x, reals lb)`**
Transforms a value `x` greater than `lb` back to unconstrained form. Available since 2.37.

### Upper Bounds

**`upper_bound_constrain(reals y, reals ub)`**
Maps unconstrained `y` to a value less than upper bound `ub`. Available since 2.37.

**`upper_bound_jacobian(reals y, reals ub)`**
Constrains `y` below `ub` while updating the Jacobian. Available since 2.37.

**`upper_bound_unconstrain(reals x, reals ub)`**
Unconstrains a value `x` less than `ub`. Available since 2.37.

### Upper and Lower Bounds

**`lower_upper_bound_constrain(reals y, reals lb, reals ub)`**
Constrains `y` between lower bound `lb` and upper bound `ub`. Available since 2.37.

**`lower_upper_bound_jacobian(reals y, reals lb, reals ub)`**
Applies bounds while incrementing the Jacobian. Available since 2.37.

**`lower_upper_bound_unconstrain(reals x, reals lb, reals ub)`**
Unconstrains bounded value `x`. Available since 2.37.

### Affine Transforms

**`offset_multiplier_constrain(reals y, reals offset, reals mult)`**
Applies scaling `mult` and shift `offset` to value `y`. Available since 2.37.

**`offset_multiplier_jacobian(reals y, reals offset, reals mult)`**
Performs affine transformation while updating Jacobian. Available since 2.37.

**`offset_multiplier_unconstrain(reals x, reals offset, reals mult)`**
Reverses the scaling and shifting. Available since 2.37.

## Transforms for Constrained Vectors

These functions constrain entire vectors. Some transforms change vector length.

### Ordered Vectors

**`ordered_constrain(vectors y)`**
Returns a vector with elements in ascending order. Available since 2.37.

**`ordered_jacobian(vectors y)`**
Produces ordered vector while adjusting Jacobian. Available since 2.37.

**`ordered_unconstrain(vectors x)`**
Unconstrains an ordered vector. Available since 2.37.

### Positive Ordered Vectors

**`positive_ordered_constrain(vectors y)`**
Returns a vector with positive elements in ascending order. Available since 2.37.

**`positive_ordered_jacobian(vectors y)`**
Constrains to positive ordered form with Jacobian adjustment. Available since 2.37.

**`positive_ordered_unconstrain(vectors x)`**
Unconstrains a positive ordered vector. Available since 2.37.

### Simplexes

**`simplex_constrain(vectors y)`**
Maps free vector `y` to simplex (elements sum to 1, each between 0 and 1). Output has one extra element. Available since 2.37.

**`simplex_jacobian(vectors y)`**
Constrains to simplex with Jacobian incrementation. Output size is input size plus one. Available since 2.37.

**`simplex_unconstrain(vectors x)`**
Unconstrains a simplex vector. Output is one element shorter. Available since 2.37.

### Sum-to-Zero Vectors

**`sum_to_zero_constrain(vectors y)`**
Produces a vector where elements sum to zero. Output has one extra element. Available since 2.37.

**`sum_to_zero_jacobian(vectors y)`**
Constrains to sum-to-zero form with Jacobian adjustment. Available since 2.37.

**`sum_to_zero_unconstrain(vectors x)`**
Unconstrains a sum-to-zero vector. Output is one element shorter. Available since 2.37.

### Unit Vectors

**`unit_vectors_constrain(vectors y)`**
Returns a unit-length vector. Rejects if input has zero or non-finite norm. Available since 2.37.

**`unit_vectors_jacobian(vectors y)`**
Produces unit vector with Jacobian adjustment. Rejects zero vectors. Available since 2.37.

**`unit_vectors_unconstrain(vectors x)`**
Unconstrains a unit vector. Available since 2.37.

## Transforms for Constrained Matrices

### Cholesky Factors of Correlation Matrices

**`cholesky_factor_corr_constrain(vectors y, int K)`**
Maps vector `y` (length equal to K choose 2) to a KxK Cholesky factor of a correlation matrix with unit-length rows. Available since 2.37.

**`cholesky_factor_corr_jacobian(vectors y, int K)`**
Produces Cholesky correlation factor with Jacobian adjustment. Available since 2.37.

**`cholesky_factor_corr_unconstrain(matrices x)`**
Unconstrains a Cholesky factor of correlation matrix to a free vector. Available since 2.37.

### Cholesky Factors of Covariance Matrices

**`cholesky_factor_cov_constrain(vectors y, int M, int N)`**
Maps free vector `y` to an MxN Cholesky factor of a covariance matrix. Vector length must be N + (N choose 2) + (M-N)*N. Available since 2.37.

**`cholesky_factor_cov_jacobian(vectors y, int M, int N)`**
Produces Cholesky covariance factor with Jacobian adjustment. Available since 2.37.

**`cholesky_factor_cov_unconstrain(matrices x)`**
Unconstrains an MxN Cholesky covariance factor. Available since 2.37.

### Correlation Matrices

**`corr_matrix_constrain(vectors y, int K)`**
Maps vector `y` (length K choose 2) to a KxK correlation matrix. Available since 2.37.

**`corr_matrix_jacobian(vectors y, int K)`**
Produces correlation matrix with Jacobian adjustment. Available since 2.37.

**`corr_matrix_unconstrain(matrices x)`**
Unconstrains a KxK correlation matrix. Available since 2.37.

### Covariance Matrices

**`cov_matrix_constrain(vectors y, int K)`**
Maps vector `y` (length K + K choose 2) to a KxK covariance matrix. Available since 2.37.

**`cov_matrix_jacobian(vectors y, int K)`**
Produces covariance matrix with Jacobian incrementation. Available since 2.37.

**`cov_matrix_unconstrain(matrices x)`**
Unconstrains a KxK positive definite matrix. Available since 2.37.

### Column-Stochastic Matrices

**`stochastic_column_constrain(matrices y)`**
Maps free NxM matrix to left stochastic (N+1)xM matrix where each column is a simplex. Available since 2.37.

**`stochastic_column_jacobian(matrices y)`**
Produces column-stochastic matrix with Jacobian adjustment. Available since 2.37.

**`stochastic_column_unconstrain(matrices x)`**
Unconstrains left stochastic matrix. Available since 2.37.

### Row-Stochastic Matrices

**`stochastic_row_constrain(matrices y)`**
Maps free NxM matrix to right stochastic Nx(M+1) matrix where each row is a simplex. Available since 2.37.

**`stochastic_row_jacobian(matrices y)`**
Produces row-stochastic matrix with Jacobian adjustment. Available since 2.37.

**`stochastic_row_unconstrain(matrices x)`**
Unconstrains right stochastic matrix. Available since 2.37.

### Sum-to-Zero Matrices

**`sum_to_zero_constrain(matrices y)`**
Maps unconstrained NxM matrix to (N+1)x(M+1) matrix with zero row and column sums. Available since 2.37.

**`sum_to_zero_jacobian(matrices y)`**
Identical to constraining function (Jacobian incrementation is zero). Available since 2.37.

**`sum_to_zero_unconstrain(matrices x)`**
Unconstrains sum-to-zero matrix to have one fewer row and column. Available since 2.37.

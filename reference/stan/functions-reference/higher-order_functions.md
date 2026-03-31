# Stan Higher-Order Functions Documentation

## Overview

Stan provides higher-order functions that operate on other functions as arguments. These include algebraic equation solvers, differential equation solvers, integrators, and parallel computation functions.

## Algebraic Equation Solvers

### Function Specification

An algebraic system must return a `vector` with signature:
```
vector algebra_system (vector y, ...)
```

The first argument represents unknowns to solve for; additional arguments are variadic and can be marked as `data` to optimize gradient computation.

### Available Solvers

**Newton's Method:**
- `solve_newton(function algebra_system, vector y_guess, ...)`
- `solve_newton_tol(function algebra_system, vector y_guess, data real scaling_step, data real f_tol, int max_steps, ...)`

**Powell's Hybrid Method:**
- `solve_powell(function algebra_system, vector y_guess, ...)`
- `solve_powell_tol(function algebra_system, vector y_guess, data real rel_tol, data real f_tol, int max_steps, ...)`

### Control Parameters

- `scaling_step`: Newton solver only, default 10^-3
- `rel_tol`: Powell solver only, default 10^-10
- `function_tol`: Default 10^-6
- `max_num_steps`: Default 200

## Ordinary Differential Equation Solvers

### Non-Stiff Methods

**Dormand-Prince (RK45):**
- `ode_rk45(function ode, vector initial_state, real initial_time, array[] real times, ...)`
- `ode_rk45_tol(function ode, vector initial_state, real initial_time, array[] real times, data real rel_tol, data real abs_tol, int max_num_steps, ...)`

**Cash-Karp (CKRK):**
- `ode_ckrk(function ode, vector initial_state, real initial_time, array[] real times, ...)`
- `ode_ckrk_tol(..., data real rel_tol, data real abs_tol, int max_num_steps, ...)`

**Adams-Moulton:**
- `ode_adams(function ode, vector initial_state, real initial_time, array[] real times, ...)`
- `ode_adams_tol(..., data real rel_tol, data real abs_tol, int max_num_steps, ...)`

### Stiff Method

**Backward Differentiation Formula:**
- `ode_bdf(function ode, vector initial_state, real initial_time, array[] real times, ...)`
- `ode_bdf_tol(..., data real rel_tol, data real abs_tol, int max_num_steps, ...)`

### Adjoint Solver

`ode_adjoint_tol_ctl(function ode, vector initial_state, real initial_time, array[] real times, data real rel_tol_forward, data vector abs_tol_forward, data real rel_tol_backward, data vector abs_tol_backward, int max_num_steps, int num_steps_between_checkpoints, int interpolation_polynomial, int solver_forward, int solver_backward, ...)`

### ODE System Function Signature

```
vector ode(real time, vector state, ...)
```

Returns state derivatives; output length must match state input length.

## Differential-Algebraic Equation Solvers

### Available Functions

- `dae(function residual, vector initial_state, vector initial_state_derivative, data real initial_time, data array[] real times, ...)`
- `dae_tol(function residual, vector initial_state, vector initial_state_derivative, data real initial_time, data array[] real times, data real rel_tol, data real abs_tol, int max_num_steps, ...)`

### DAE System Function Signature

```
vector residual(real time, vector state, vector state_derivative, ...)
```

Returns residuals at specified time and state; length must match state vectors.

### Key Requirement

Users must ensure initial conditions satisfy the residual function: it becomes zero at t_0 when initial state and state derivative are provided.

## 1D Integration

### Integrand Function Signature

```
real integrand(real x, real xc, array[] real theta,
               array[] real x_r, array[] int x_i)
```

Arguments represent: integration point, high-precision distance to endpoint, parameters, real data, and integer data.

### Integration Functions

- `integrate_1d(function integrand, real a, real b, array[] real theta, array[] real x_r, array[] int x_i)`
- `integrate_1d(function integrand, real a, real b, array[] real theta, array[] real x_r, array[] int x_i, real relative_tolerance)`

The integrator automatically splits zero-crossing integrals into separate regions for numeric stability. The `xc` parameter provides high-precision distances near integration limits to mitigate precision loss in definite integrals.

## Reduce-Sum Function

Performs parallel summation by computing partial sums of array elements.

### Functions

- `reduce_sum(F f, array[] T x, int grainsize, T1 s1, T2 s2, ...)`
- `reduce_sum_static(F f, array[] T x, int grainsize, T1 s1, T2 s2, ...)`

`reduce_sum` uses dynamic scheduling; `reduce_sum_static` provides consistent partitioning across runs.

### Partial Sum Function Signature

```
(array[] T x_subset, int start, int end, T1 s1, T2 s2, ...):real
```

Returns the sum from start to end indices (inclusive). Shared arguments remain consistent across partial sums.

## Map-Rect Function

Provides map-reduce functionality for rectangular data structures.

### Function Signature

```
vector f(vector phi, vector theta,
         data array[] real x_r, data array[] int x_i)
```

Arguments represent: shared parameters, shard-specific parameters, shard-specific real data, and shard-specific integer data.

### Rectangular Map Function

`map_rect(F f, vector phi, array[] vector theta, data array[,] real x_r, data array[,] int x_i)`

Applies function `f` elementwise: `f(phi, theta[n], x_r[n], x_i[n])` for each n, concatenating results.

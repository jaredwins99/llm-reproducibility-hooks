# Deprecated Functions - Stan 2.38

## Overview

This page documents currently deprecated functionality in Stan along with replacement approaches. Starting in Stan 2.29, deprecated functions with direct replacements will be removed 3 versions after deprecation.

"The Stan compiler can automatically update these on the behalf of the user for the entire deprecation window and at least one version following the removal."

## Integer Division with `operator/`

**Status:** Deprecated

**Issue:** Using `/` with two integer arguments performs integer floor division, where `1 / 2 = 0`. This contrasts with real division where `1.0 / 2.0 = 0.5`, creating confusion.

**Solution:** Use the integer division operator `operator%/%` instead.

## ODE Integrators (integrate_ode_rk45, integrate_ode_adams, integrate_ode_bdf)

These functions have been replaced by solvers in the Ordinary Differential Equation (ODE) Solvers section.

### ODE Function Specification

An ODE system requires a function with this signature:

```
array[] real ode(real time, array[] real state, array[] real theta,
                 array[] real x_r, array[] int x_i)
```

Parameters:
- **time:** evaluation point
- **state:** system state at specified time
- **theta:** parameter values
- **x_r:** real data values
- **x_i:** integer data values

### Non-Stiff Solver

`array[,] real integrate_ode_rk45(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, array[] real x_r, array[] int x_i)`

Uses Dormand-Prince algorithm (4th/5th order Runge-Kutta). *Available since 2.10, deprecated in 2.24*

`array[,] real integrate_ode_rk45(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, array[] real x_r, array[] int x_i, real rel_tol, real abs_tol, int max_num_steps)`

Variant with solver control parameters. *Available since 2.10, deprecated in 2.24*

`array[,] real integrate_ode(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, array[] real x_r, array[] int x_i)`

Dormand-Prince method. *Available since 2.10, deprecated in 2.24*

`array[,] real integrate_ode_adams(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, data array[] real x_r, data array[] int x_i)`

Adams-Moulton method. *Available since 2.23, deprecated in 2.24*

`array[,] real integrate_ode_adams(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, data array[] real x_r, data array[] int x_i, data real rel_tol, data real abs_tol, data int max_num_steps)`

Adams-Moulton with control parameters. *Available since 2.23, deprecated in 2.24*

### Stiff Solver

`array[,] real integrate_ode_bdf(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, data array[] real x_r, data array[] int x_i)`

Backward differentiation formula method. *Available since 2.10, deprecated in 2.24*

`array[,] real integrate_ode_bdf(function ode, array[] real initial_state, real initial_time, array[] real times, array[] real theta, data array[] real x_r, data array[] int x_i, data real rel_tol, data real abs_tol, data int max_num_steps)`

BDF with control parameters. *Available since 2.10, deprecated in 2.24*

### ODE Solver Arguments

- **ode:** function with signature `(real, array[] real, array[] real, data array[] real, data array[] int):array[] real`
- **initial_state:** type `array[] real`
- **initial_time:** type `int` or `real`
- **times:** type `array[] real`
- **theta:** type `array[] real`
- **data x_r:** type `array[] real` (data only)
- **data x_i:** type `array[] int` (data only)

Optional parameters:
- **data rel_tol:** relative tolerance, type `real`
- **data abs_tol:** absolute tolerance, type `real`
- **data max_num_steps:** maximum steps, type `int`

**Return Value:** `array[,] real` containing solutions at specified times.

## Algebraic Solvers (algebra_solver, algebra_solver_newton)

These have been replaced by solvers in the Algebraic Equation Solvers section.

### Algebraic System Specification

Required function signature:

```
vector algebra_system(vector y, vector theta,
                      data array[] real x_r, array[] int x_i)
```

Parameters:
- **y:** unknowns to solve
- **theta:** parameter values
- **x_r:** real data values
- **x_i:** integer data values

### Solver Functions

`vector algebra_solver(function algebra_system, vector y_guess, vector theta, data array[] real x_r, array[] int x_i)`

Powell hybrid algorithm. *Available since 2.17, deprecated in 2.31*

`vector algebra_solver(function algebra_system, vector y_guess, vector theta, data array[] real x_r, array[] int x_i, data real rel_tol, data real f_tol, int max_steps)`

Powell hybrid with control parameters. *Available since 2.17, deprecated in 2.31*

`vector algebra_solver_newton(function algebra_system, vector y_guess, vector theta, data array[] real x_r, array[] int x_i)`

Newton's method. *Available since 2.24, deprecated in 2.31*

`vector algebra_solver_newton(function algebra_system, vector y_guess, vector theta, data array[] real x_r, array[] int x_i, data real rel_tol, data real f_tol, int max_steps)`

Newton's method with control parameters. *Available since 2.24, deprecated in 2.31*

### Algebraic Solver Arguments

- **algebra_system:** function with signature `(vector, vector, array[] real, array[] int):vector`
- **y_guess:** initial guess, type `vector`
- **theta:** parameters, type `vector`
- **x_r:** real data, type `array[] real`
- **x_i:** integer data, type `array[] int`

Optional parameters:
- **rel_tol:** relative tolerance, type `real`
- **function_tol:** function tolerance, type `real`
- **max_num_steps:** maximum steps, type `int`

**Return Value:** `vector` where values make the algebraic function equal zero.

# Solving Algebraic Equations in Stan

## Overview

Stan provides built-in algebraic equation solvers using either Newton's method (via Kinsol) or Powell's hybrid method. These tools convert algebraic systems into root-finding problems where you seek values making f(y) = 0.

## Key Concepts

**Problem Structure**: The documentation presents a nonlinear system example:
- z1 = y1 - theta1
- z2 = y1 * y2 + theta2

The goal involves simultaneously solving for unknowns y1 and y2 such that the output vector approaches zero.

## Implementation

**Function Signature**: Systems require a strictly defined function structure:

```stan
vector system(vector y, vector theta, data array[] real x_r, array[] int x_i)
```

This function must return a vector where all components equal zero at the solution. The signature is mandatory even when parameters or data aren't used.

**Example Code**: For the sample system with theta = (3, 6):

```stan
transformed data {
  vector[2] y_guess = [1, 1]';
  array[0] real x_r;
  array[0] int x_i;
}

transformed parameters {
  vector[2] theta = [3, 6]';
  vector[2] y;
  y = solve_newton(system, y_guess, theta, x_r, x_i);
}
```

This returns y = (3, -2).

## Critical Constraints

- The Jacobian matrix must be square (number of equations = number of unknowns)
- Real data and integer data arguments must involve only data variables
- Parameters can only appear in theta
- Initial guesses significantly affect convergence

## Control Parameters

The `_tol` solver variant accepts three tuning arguments before variadic parameters:

```stan
y = solve_newton_tol(system, y_guess, scaling_step, f_tol, max_steps,
                     theta, x_r, x_i);
```

**Default values**:
- scaling_step: 1e-3
- function tolerance (f_tol): 1e-6
- maximum steps: 200

## Tolerance Considerations

Function tolerance represents the norm of the algebraic function at the proposed solution -- ideally approaching zero. As problem dimension increases, meeting specified tolerances becomes progressively harder since each vector element contributes to the overall norm.

## Failure Modes

- **No convergence**: Occurs when systems lack solutions in parameter space; the MCMC proposal gets rejected
- **Degenerate systems**: Multiple solutions may exist; initial guesses determine which solution is found first
- **Step limit exceeded**: Running solvers terminate and reject proposals if maximum iterations are reached

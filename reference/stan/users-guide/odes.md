# Ordinary Differential Equations in Stan

## Overview

Stan provides multiple methods for solving systems of ordinary differential equations (ODEs). All solvers adaptively refine solutions to meet specified tolerances. The key computational challenge involves calculating gradients of ODE solutions with respect to parameters---essential for Stan's gradient-based algorithms.

## Two Sensitivity Approaches

**Forward sensitivity:** Expands the base ODE system by adding N sensitivity states per parameter, resulting in N + N*M total states. Computational cost scales multiplicatively with states and parameters.

**Adjoint sensitivity:** Solves the base system forward (N states), then solves backward in time (N states) with M quadrature equations. Cost scales linearly in both dimensions, offering better performance for problems with many parameters.

## Available Solvers

Stan provides four forward solvers suited to different problem types:

- **rk45**: Fourth/fifth-order Runge-Kutta for non-stiff systems (start here if uncertain)
- **bdf**: Variable-step, variable-order backward-differentiation formula for stiff systems
- **adams**: Variable-step Adams-Moulton formula for non-stiff, smooth solutions requiring high accuracy
- **ckrk**: Fourth/fifth-order explicit Runge-Kutta for semi-stiff systems with rapidly varying solutions

## ODE System Function Requirements

System functions must follow a strict signature:

```stan
vector system_function(real t, vector y, real theta) {
  // Additional arguments allowed
  vector[n] dydt;
  // compute derivatives
  return dydt;
}
```

The first argument is time (real), second is state (vector), return type is vector. Additional arguments can be any Stan type, matching the solver call exactly.

## Example: Simple Harmonic Oscillator

```stan
vector sho(real t, vector y, real theta) {
  vector[2] dydt;
  dydt[1] = y[2];
  dydt[2] = -y[1] - theta * y[2];
  return dydt;
}
```

This models a damped oscillator where friction coefficient theta affects velocity-dependent damping.

## Calling ODE Solvers

Basic syntax for forward solvers:

```stan
array[T] vector[2] y_sim = ode_rk45(sho, y0, t0, ts, theta);
```

With control parameters:

```stan
array[T] vector[2] y_sim = ode_rk45_tol(sho, y0, t0, ts,
                                         rel_tol,
                                         abs_tol,
                                         max_steps,
                                         theta);
```

Control parameters must be data variables, not parameters or parameter-dependent expressions.

## Measurement Error Models

ODE solutions can be combined with observation models to estimate system parameters:

```stan
model {
  array[T] vector[2] mu = ode_rk45(sho, y0, t0, ts, theta);
  sigma ~ normal(0, 2.5);
  theta ~ std_normal();
  y0 ~ std_normal();
  for (t in 1:T) {
    y[t] ~ normal(mu[t], sigma);
  }
}
```

## Stiff ODE Systems

Stiffness occurs in systems with vastly different time scales (common in chemical reactions). Use `bdf` instead of `rk45` for stiff systems. When uncertain, benchmark both solvers.

## Tolerance Selection

Tolerances control estimated local error through a weighted root-mean-square norm:

$$\sqrt{\sum_{i=1}^n{\frac{1}{n}\frac{e_i^2}{(\text{RTOL}\times y_i + \text{ATOL})^2}}} < 1$$

- **Relative tolerance (RTOL):** Dominates when |y_i| >> 1
- **Absolute tolerance (ATOL):** Critical when y_i approaches zero

Default values: rk45/ckrk use 10^-6 for both; bdf/adams use 10^-10. Maximum steps default to 1 million (rk45/ckrk) or 100 million (bdf/adams).

## Discontinuous ODE Functions

When discontinuities exist, integrate separately on either side rather than attempting to cross them. Use conditional logic to handle events like lag periods in pharmacokinetic models.

## Adjoint Sensitivity Solver

For problems with many parameters, use adjoint methods:

```stan
array[T] vector[2] y_sim = ode_adjoint_tol_ctl(
    sho, y0, t0, ts,
    rel_tol_fwd, abs_tol_fwd,     // forward phase
    rel_tol_bwd, abs_tol_bwd,     // backward phase
    rel_tol_quad, abs_tol_quad,   // quadrature
    max_steps, num_checkpoints,
    interp_type, fwd_solver, bwd_solver,
    theta);
```

Adjoint methods require careful configuration but scale better with parameter count.

## Linear ODEs via Matrix Exponential

For linear systems dy/dt = A*y, use matrix exponential for efficiency:

$$y = e^{tA} \cdot y_0$$

```stan
generated quantities {
  matrix[2, 2] A = [[0, 1], [-1, -theta[1]]];
  for (t in 1:T) {
    y_sim[t] = matrix_exp((t - 1) * A) * y0;
  }
}
```

This approach is considerably faster than numerical ODE solvers for linear systems.

## Key Recommendations

- Start with `rk45` unless problem characteristics suggest otherwise
- Choose tolerances based on solution scales and measurement precision
- For uncertain stiffness, benchmark with both `rk45` and `bdf`
- Integrate discontinuous systems separately at transition points
- Use adjoint solvers primarily for large parameter spaces where forward sensitivity becomes prohibitive

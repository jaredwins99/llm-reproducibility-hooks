# Differential-Algebraic Equations

## Overview

Stan supports solving systems of differential-algebraic equations (DAEs) of index 1. These systems combine differential equations with algebraic constraints, where variable derivatives may be implicitly constrained rather than explicitly expressed like in ODEs.

The solver uses forward sensitivity calculations to compute gradients of the DAE solution with respect to parameters, expanding the base system with additional sensitivity equations. For each parameter, N additional sensitivity states are added, creating a full system of N + N*M states.

## Key Concepts

### What are DAEs?

A DAE system is defined by residual functions r(y', y, t, theta) = 0, with consistent initial conditions y(t0, theta) = y0 and y'(t0, theta) = y'0. The theta notation emphasizes that solutions depend on parameters used in the computation.

### Index of DAEs

The index represents the minimum number of differentiations needed to convert a DAE into an ODE. Stan's solver supports only index-1 DAEs. Higher-index problems must be analytically converted to lower-index systems first.

## Example: Chemical Kinetics

A practical example involves the Robertson chemical kinetics problem with two differential equations and one algebraic constraint:

- dy1/dt + alpha*y1 - beta*y2*y3 = 0
- dy2/dt - alpha*y1 + beta*y2*y3 + gamma*y2^2 = 0
- y1 + y2 + y3 - 1.0 = 0

This system requires consistent initial conditions satisfying r(y'(t0), y(t0), t0) = 0.

## Coding DAE Systems

### Function Signature

The DAE residual function requires a strict signature:

```stan
vector function_name(real t, vector y, vector yp, ...)
```

Where:
- First argument: time (real)
- Second argument: system state (vector)
- Third argument: state derivative (vector)
- Return value: residuals (vector)
- Additional arguments: parameters, data, or other quantities

### Example Implementation

```stan
vector chem(real t, vector yy, vector yp,
            real alpha, real beta, real gamma) {
  vector[3] res;
  res[1] = yp[1] + alpha * yy[1] - beta * yy[2] * yy[3];
  res[2] = yp[2] - alpha * yy[1] + beta * yy[2] * yy[3] + gamma * yy[2] * yy[2];
  res[3] = yy[1] + yy[2] + yy[3] - 1.0;
  return res;
}
```

### Valid Signatures

These signatures are allowed:

```stan
vector my_dae1(real t, vector y, vector yp, real a0);
vector my_dae2(real t, vector y, vector yp, array[] int a0, vector a1);
vector my_dae3(real t, vector y, vector yp, matrix a0, array[] real a1, row_vector a2);
```

These are not allowed:

```stan
vector my_dae1(real t, array[] real y, vector yp);
// Second argument must be vector
array[] real my_dae2(real t, vector y, vector yp);
// Return type must be vector
vector my_dae3(real t, vector y);
// Missing required arguments
```

## Solving DAEs

### Basic Usage

```stan
data {
  int N;
  vector[3] yy0;
  vector[3] yp0;
  real t0;
  real alpha;
  real beta;
  array[N] real ts;
  array[N] vector[3] y;
}
parameters {
  real gamma;
}
transformed parameters {
  vector[3] y_hat[N] = dae(chem, yy0, yp0, t0, ts, alpha, beta, gamma);
}
```

Since gamma is a parameter, the DAE solver is called in the transformed parameters block.

### Advanced: Controlling Solver Parameters

Use `dae_tol` to specify tolerances and maximum steps:

```stan
vector[3] y_hat[N] = dae_tol(chem, yy0, yp0, t0, ts,
                             relative_tolerance,
                             absolute_tolerance,
                             max_num_steps,
                             alpha, beta, gamma);
```

Control parameters must be data variables---they cannot depend on parameters or be expressions evaluated outside transformed data and generated quantities blocks.

## Control Parameters

### Tolerances

Default values are 10^-10 for both relative and absolute tolerances. Users should select tolerances based on:

- Solution scales
- Required accuracy
- How solutions are used in the model

### Maximum Number of Steps

Defaults to 100 million steps. This parameter helps prevent runaway simulations when MCMC explores parameter space far from typical solution regions, particularly during warmup in stiff regions.

## Implementation Details

Internally, Stan's DAE solver uses a variable-step, variable-order backward-differentiation formula implementation based on IDAS (the sensitivity-enabled DAE solver in SUNDIALS).

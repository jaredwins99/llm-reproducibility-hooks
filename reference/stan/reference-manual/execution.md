# Program Execution in Stan

## Overview

According to the Stan Reference Manual, "This chapter provides a sketch of how a compiled Stan model is executed using sampling. Optimization shares the same data reading and initialization steps, but then does optimization rather than sampling."

## Reading and Transforming Data

### Data Input Stage

The initial execution phase involves loading data into memory through files (CmdStan) or memory interfaces (RStan, PyStan). All variables declared in the `data` block are read, and the program halts if any required variable is missing.

Constraint validation occurs immediately after each variable is read. For example, a variable declared as `int<lower=0>` is tested to ensure non-negativity. Violations trigger an error message identifying the problematic variable, its value, and the violated constraint.

### Transformed Data Definition

After data loading, transformed data variable statements execute sequentially. Constraints on transformed data are not enforced during execution but are validated afterward. Real values initialize to `NaN` and integers to a large negative number.

If post-execution validation fails, the program halts with diagnostic information about the variable, its computed value, and declared constraints.

## Initialization

### User-Supplied Initial Values

User-provided initial values use the same input mechanism as data. Parameter constraints are validated against these values. The description warns that "initializing parameters on the boundaries of their constraints is usually problematic," as boundary values transform to infinite unconstrained values, causing infinite Jacobians and failed probability calculations.

### Random Initialization

Default initialization draws unconstrained parameters uniformly from the interval (-2, 2). This symmetric range centers on 0, representing the initialization median. An unconstrained value of 0 maps to different constrained values depending on parameter declarations:

- **Unconstrained reals**: No transformation; 0 remains 0
- **Parameters bounded below at 0**: 0 unconstrained corresponds to exp(0) = 1 constrained
- **Probability parameters** (0,1 bounds): 0 unconstrained corresponds to 0.5 constrained via inverse logit
- **Simplexes**: 0 unconstrained yields symmetric constrained values (1/K for K-simplexes)
- **Cholesky factors**: Initialize diagonals to 1, below-diagonal elements to 0

### Zero Initialization

All parameters may initialize to 0 on the unconstrained scale, useful for diagnosis or as a sampling starting point. Multiple chains with diffuse starting points help assess convergence.

## Sampling Process

### Hamiltonian Mechanics

Sampling simulates Hamiltonian dynamics with particle position representing current parameters and randomly generated momentum. The potential energy equals the negative log unnormalized probability function from the model. The leapfrog integrator discretizes the smooth trajectory into small time steps.

### Leapfrog Steps

Each leapfrog step requires evaluating both the negative log probability function and its gradient. These values update momentum (based on gradient) and position (based on momentum). Simple models need few large steps; complex posteriors require many small steps.

Users can specify step count (standard HMC) or allow the No-U-Turn Sampler (NUTS) to determine steps adaptively.

### Log Probability and Gradient Computation

During each leapfrog step, calculating the log probability and gradients consumes the most computational time. This calculation occurs over unconstrained parameters through these steps:

1. Inverse transform unconstrained parameters to constrained form
2. Add the log Jacobian of the inverse transform to accumulated log probability
3. Execute transformed parameter statements and validate their constraints
4. Execute model block statements

The accumulated expression tree is then used for gradient calculation via backward propagation of partial derivatives.

### Metropolis Accept/Reject

A standard Metropolis adjustment maintains detailed balance and ensures marginal distribution agreement with the model. This step compares log probabilities (Hamiltonians), which sum potential (negative log probability) and kinetic (squared momentum) energies.

Theory suggests the Hamiltonian remains invariant and rejection should never occur. Practically, rejection probability depends on leapfrog approximation accuracy. Step size balance matters: small steps minimize rejections but require more steps for distance; large steps do the opposite. Stan tunes step size during warmup to achieve desired rejection rates when users don't specify one.

## Optimization

Optimization follows data reading and parameter initialization like sampling but produces deterministic output requiring only convergence verification. Output format resembles sampling results.

## Variational Inference

Variational inference similarly reads data and initializes parameters. Initial approximations draw from standard normal distributions in unconstrained space. Upon convergence, it outputs draws from the approximate posterior, allowing use of standard sampling analysis tools.

## Model Diagnostics

Diagnostics depend on data reading and parameter initialization. Available diagnostics include gradients on the unconstrained scale and log probabilities, with interface-specific guides (RStan, PyStan, CmdStan) providing additional details.

## Output Stage

### Generated Quantities Execution

Before output, generated quantities block statements execute, enabling forward simulation based on model parameters or parameter transformation for output purposes. Declared constraints on generated quantities are validated post-execution, with violations triggering termination with diagnostic messages.

### Final Output Writing

The final step writes values for all parameters, transformed parameters, and generated quantities in their constrained forms. Local variables, data, and transformed data are excluded. Values are written in comma-separated value (CSV) format with headers naming all parameters, including indices for multivariate parameters.

---

**Reference:**
Hoffman, M. D., & Gelman, A. (2014). "The No-U-Turn Sampler: Adaptively Setting Path Lengths in Hamiltonian Monte Carlo." *Journal of Machine Learning Research*, 15, 1593-623.

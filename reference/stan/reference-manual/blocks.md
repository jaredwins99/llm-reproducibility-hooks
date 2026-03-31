# Stan Program Blocks - Complete Content

## Overview

A Stan program is structured into named blocks containing variable declarations and statements. The complete block structure includes:

```stan
functions {
  // function declarations and definitions
}
data {
  // declarations
}
transformed data {
  // declarations and statements
}
parameters {
  // declarations
}
transformed parameters {
  // declarations and statements
}
model {
  // declarations and statements
}
generated quantities {
  // declarations and statements
}
```

## Key Characteristics

**Optionality and Ordering**: All blocks are optional; an empty program is valid (though generates a warning). Blocks must appear in the specified order, with declarations preceding statements within each block.

**Variable Scope**: Variables declared in a block are accessible in all subsequent blocks. Model-block variables are local only to that block. Function parameters have function-local scope.

**Function Scope**: Functions defined in the functions block are usable in appropriate locations. Random-number-generating functions (suffixed `_rng`) are restricted to transformed data and generated quantities blocks. Log-probability modifying functions (suffixed `_lp`) are restricted to transformed parameters and model blocks.

## Block Details

### Data Block
- Declares variables read from external sources
- No statements allowed
- Variables validated against constraints upon reading
- Executed once per chain

### Transformed Data Block
- Declares variables defined through statements
- Executed once per chain after data reading
- Distribution statements not permitted
- Constraints validated after statement execution

### Parameters Block
- Declares sampling variables
- No statements allowed
- Undergoes inverse transformation to unconstrained space
- Log Jacobian of transformation added to probability function
- Gradient calculated via automatic differentiation during HMC/NUTS sampling

### Transformed Parameters Block
- Declares derived quantities from parameters and data
- Constraints serve error-checking purposes only
- Executed once per leapfrog step
- Variables included in output

### Model Block
- Contains variable declarations and statements
- Defines log probability function
- Distribution statements permitted
- Local variables cannot have constraints

### Generated Quantities Block
- Executed after sampling completes
- Enables forward sampling, prediction, posterior event probabilities, and model comparison statistics
- Independent of sampling process
- All declared variables included in output

## Variable Taxonomy

Variables are classified as:
- **Constants**: Declared in data or transformed data
- **Unmodeled data**: Declared in data or transformed data (e.g., sample sizes)
- **Modeled data**: Declared in data or transformed data but treated as random
- **Missing data**: Declared in parameters or transformed parameters
- **Modeled parameters**: Declared in parameters or transformed parameters
- **Unmodeled parameters**: Hyperparameters in data or transformed data
- **Derived quantities**: Defined in transformed data, transformed parameters, or generated quantities
- **Loop indices**: Declared in loop statements

## Block Actions Summary

| Block | Statements | Action/Period |
|-------|-----------|---------------|
| data | no | read / chain |
| transformed data | yes | evaluate / chain |
| parameters | no | inverse transform, Jacobian / leapfrog; write / sample |
| transformed parameters | yes | evaluate / leapfrog; write / sample |
| model | yes | evaluate / leapfrog step |
| generated quantities | yes | evaluate / sample; write / sample |
| (initialization) | n/a | read, transform / chain |

## Variable Declaration Guidance

Selection depends on three factors: parameter dependence, inclusion in target log probability, and output requirements:

- **Parameter-dependent + in target + save**: Use transformed parameters
- **Parameter-dependent + in target + don't save**: Use model (local)
- **Parameter-dependent + not in target + save**: Use generated quantities
- **Parameter-dependent + not in target + don't save**: Use generated quantities (local)
- **Parameter-independent + in target + save**: Use transformed data and generated quantities
- **Parameter-independent + in target + don't save**: Use transformed data
- **Parameter-independent + not in target + save**: Use generated quantities
- **Parameter-independent + not in target + don't save**: Use transformed data (local)

## Example Program

```stan
data {
  int<lower=0> N;           // unmodeled data
  array[N] real y;          // modeled data
  real mu_mu;               // unmodeled parameter
  real<lower=0> sigma_mu;   // unmodeled parameter
}
transformed data {
  real<lower=0> alpha;      // constant unmodeled parameter
  real<lower=0> beta;       // constant unmodeled parameter
  alpha = 0.1;
  beta = 0.1;
}
parameters {
  real mu_y;                // modeled parameter
  real<lower=0> tau_y;      // modeled parameter
}
transformed parameters {
  real<lower=0> sigma_y;    // derived quantity
  sigma_y = pow(tau_y, -0.5);
}
model {
  tau_y ~ gamma(alpha, beta);
  mu_y ~ normal(mu_mu, sigma_mu);
  for (n in 1:N) {
    y[n] ~ normal(mu_y, sigma_y);
  }
}
generated quantities {
  real variance_y;          // derived quantity
  variance_y = sigma_y * sigma_y;
}
```

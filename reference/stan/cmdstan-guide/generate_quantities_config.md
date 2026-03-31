# Generating Quantities of Interest from a Fitted Model

## Overview

The `generate_quantities` method enables computation of additional quantities of interest from an existing fitted model without rerunning the sampler. This involves creating a modified Stan program with an updated or new generated quantities block that specifies the new calculations. The method applies these computations across existing parameter draws from a previous model fit.

## Key Requirements

The method mandates a `fitted_params` sub-argument that references an existing Stan CSV file containing parameter values from an equivalent model (matching parameters block, same data conditioning).

## Permitted Uses

According to the documentation, the generated quantities block facilitates:

- Forward sampling for model testing via simulation
- Predictions for new data points
- Posterior event probabilities and multiple comparison calculations
- Posterior expectation computations
- Parameter transformation for reporting purposes
- Full Bayesian decision theory applications
- Log likelihood and deviance calculations for model comparison

## Practical Example

A demonstration using the Bernoulli model shows posterior predictive checks. The example program `bernoulli_ppc.stan` contains:

```stan
generated quantities {
  array[N] int y_sim;
  for (n in 1:N) {
    y_sim[n] = bernoulli_rng(theta);
  }
  real<lower=0, upper=1> theta_rep = sum(y_sim) * 1.0 / N;
}
```

### Execution Commands

Initial sampling:
```
./bernoulli sample data file=bernoulli.data.json output file=bernoulli_fit.csv
```

Generating quantities:
```
./bernoulli_ppc generate_quantities fitted_params=bernoulli_fit.csv \
              data file=bernoulli.data.json \
              output file=bernoulli_ppc.csv
```

## Output Format

The resulting CSV contains exclusively variables declared in the generated quantities block. Column headers reflect parameter names and array indices (e.g., `y_sim.1`, `y_sim.2`).

### Accessing Parameter Values

To view fitted parameter values alongside generated quantities, create a copy variable:

```stan
real<lower=0, upper=1> theta_cp = theta;
```

This allows comparison between actual parameter estimates and derived quantities.

## Error Handling

**Invalid File Format:**
```
Error reading fitted param names from sample csv file <filename.csv>
```

This occurs when providing non-Stan CSV files or files lacking required parameter columns.

**Constraint Violations:**
```
Exception: lub_free: Bounded variable is 1.21397, but must be in the interval [0, 1]
```

This appears when parameter values exceed declared bounds (e.g., `theta` outside `[0, 1]`).

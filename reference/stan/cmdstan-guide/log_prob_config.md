# Extracting Log Probabilities and Gradients for Diagnostics

## Overview

CmdStan can compute and return the log probability and gradient values with respect to parameters. This feature is distinct from the `diagnose` subcommand and uses a different output format without finite difference comparisons.

**Important Note**: "Startup and data initialization costs mean that this method is not an efficient way to calculate these quantities. It is provided only for convenience and should not be used for serious computation."

## Configuration

The method accepts three arguments:

### jacobian
Controls whether the Jacobian adjustment for constrained parameters is included in the gradient calculation. The default setting is `true` (adjustment is included).

### constrained_params
Specifies an input file containing parameter values on the constrained scale. A single set of constrained parameters can be provided using JSON format, or alternatively, multiple draws in StanCSV format.

### unconstrained_params
Specifies an input file (JSON or R dump format) with parameter values on the unconstrained scale. The file must contain a single variable named `params_r`, which is a flattened vector of all unconstrained parameters. Two-dimensional objects are supported, with each entry being a vector of identical form, producing multiple output rows.

**Constraint**: Only one of `constrained_params` or `unconstrained_params` may be specified.

For additional information on parameter transformations, refer to the Stan reference manual section on variable transforms.

## CSV Output Format

Output files contain:

- Configuration options as CSV comments at the beginning
- Column headers with `lp__` as the first column, followed by parameter names (unconstrained parameters, regardless of input type)
- Values representing the log density and gradient with respect to each parameter

## Example

Given a JSON parameters file:

```json
{
    "theta" : 0.1
}
```

Execute the command:

```
/bernoulli log_prob constrained_params=params.json data file=bernoulli.data.json
```

This produces output similar to:

```
# method = log_prob
#   log_prob
#     unconstrained_params =  (Default)
#     constrained_params = params.json
#     jacobian = true (Default)
# id = 1 (Default)
# data
#   file = bernoulli.data.json
# init = 2 (Default)
# random
#   seed = 2390820139 (Default)
# output
#   file = output.csv (Default)
#   diagnostic_file =  (Default)
#   refresh = 100 (Default)
#   sig_figs = 8 (Default)
#   profile_file = profile.csv (Default)
# num_threads = 1 (Default)
lp_,theta
-7.856,1.8
```

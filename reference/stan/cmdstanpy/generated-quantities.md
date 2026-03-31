# CmdStanPy Generated Quantities

## Overview

The `generated quantities` block in a Stan program computes values based on data, transformed data, parameters, and transformed parameters. Use cases include:

- Forward sampling for model testing
- Generating predictions for new data
- Calculating posterior event probabilities
- Computing posterior expectations
- Transforming parameters for reporting
- Applying Bayesian decision theory
- Calculating log likelihoods for model comparison

## CmdStanModel.generate_quantities()

```python
gq = model.generate_quantities(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    previous_fit: Optional[Union[Fit, list[str]]] = None,
    seed: Optional[int] = None,
    gq_output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    mcmc_sample: Optional[Union[CmdStanMCMC, list[str]]] = None,
)
```

**Parameters:**
- `data` - The data used to fit the model
- `previous_fit` - A `CmdStanMCMC`, `CmdStanVB`, or `CmdStanMLE` object, or a list of Stan CSV files

**Returns:** `CmdStanGQ[Fit]`

The returned `CmdStanGQ` object contains values for all variables in the generated quantities block. Unlike sampling output, it excludes joint log probability density, sampler state, or parameter values.

## CmdStanGQ Properties

| Property | Description |
|----------|-------------|
| `chain_ids` | Chain identifiers |
| `chains` | Number of chains |
| `column_names` | Column names |
| `metadata` | Metadata object |

## CmdStanGQ Methods

| Method | Description |
|--------|-------------|
| `draws()` | Returns array of generated quantity draws with shape (iterations, chains, variables) |
| `draws_pd(inc_sample=True)` | Returns pandas DataFrame combining input drawset with generated quantities |
| `draws_xr()` | Returns xarray Dataset |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

## Practical Example

Adding posterior predictive checks to a Bernoulli model by generating replicate data `y_rep` using posterior estimates of parameter `theta`:

```python
import os
from cmdstanpy import CmdStanModel, cmdstan_path

# First, fit the model with MCMC
bernoulli_dir = os.path.join(cmdstan_path(), 'examples', 'bernoulli')
stan_file = os.path.join(bernoulli_dir, 'bernoulli.stan')
data_file = os.path.join(bernoulli_dir, 'bernoulli.data.json')

model = CmdStanModel(stan_file=stan_file)
fit = model.sample(data=data_file)

# Then generate quantities using the posterior draws
gq_model = CmdStanModel(stan_file='bernoulli_ppc.stan')
gq = gq_model.generate_quantities(data=data_file, previous_fit=fit)

# Access the generated quantities
gq.draws_pd(inc_sample=True)
```

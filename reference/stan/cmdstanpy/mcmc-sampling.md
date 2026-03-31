# CmdStanPy MCMC Sampling

## Overview

CmdStanPy's MCMC sampler implements Hamiltonian Monte Carlo (HMC) and the no-U-turn sampler (NUTS), generating posterior distribution draws for Bayesian inference. The `CmdStanModel.sample()` method wraps CmdStan's sampling functionality and returns a `CmdStanMCMC` object.

## CmdStanModel.sample()

```python
fit = model.sample(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    chains: Optional[int] = None,
    parallel_chains: Optional[int] = None,
    threads_per_chain: Optional[int] = None,
    seed: Optional[Union[int, list[int]]] = None,
    chain_ids: Optional[Union[int, list[int]]] = None,
    inits: Optional[Union[Mapping, float, str, list[str], list[Mapping]]] = None,
    iter_warmup: Optional[int] = None,
    iter_sampling: Optional[int] = None,
    save_warmup: bool = False,
    thin: Optional[int] = None,
    max_treedepth: Optional[int] = None,
    metric: Optional[Union[str, dict, list[str], list[dict]]] = None,
    inv_metric: Optional[Union[str, ndarray, Mapping, list[Union[str, ndarray, Mapping]]]] = None,
    step_size: Optional[Union[float, list[float]]] = None,
    adapt_engaged: bool = True,
    adapt_delta: Optional[float] = None,
    adapt_init_phase: Optional[int] = None,
    adapt_metric_window: Optional[int] = None,
    adapt_step_size: Optional[int] = None,
    fixed_param: bool = False,
    output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    save_latent_dynamics: bool = False,
    save_profile: bool = False,
    show_progress: bool = True,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    force_one_process_per_chain: Optional[bool] = None,
)
```

**Returns:** `CmdStanMCMC`

## Basic Usage

```python
import os
from cmdstanpy import CmdStanModel, cmdstan_path

bernoulli_dir = os.path.join(cmdstan_path(), 'examples', 'bernoulli')
stan_file = os.path.join(bernoulli_dir, 'bernoulli.stan')
data_file = os.path.join(bernoulli_dir, 'bernoulli.data.json')

model = CmdStanModel(stan_file=stan_file)
fit = model.sample(data=data_file)
```

## Multi-Threading Compilation

```python
model = CmdStanModel(
    stan_file='model.stan',
    cpp_options={'STAN_THREADS': 'TRUE'},
    force_compile=True,
)
```

## Data Access Methods

### Extracting Draws as Structured Variables

| Method | Description |
|--------|-------------|
| `stan_variable(name)` | Returns `numpy.ndarray` for a specific variable |
| `stan_variables()` | Returns `dict` of all Stan variables |
| `draws_xr(variable_name)` | Returns `xarray.Dataset` |

### Tabular Format Access

| Method | Description |
|--------|-------------|
| `draws()` | Returns 3-D numpy array (iterations, chains, variables) |
| `draws_pd()` | Returns `pandas.DataFrame` |

### Diagnostics

| Method | Description |
|--------|-------------|
| `method_variables()` | Returns dict with sampler diagnostics (`lp__`, `accept_stat__`, `stepsize__`, `treedepth__`, `n_leapfrog__`, `divergent__`, `energy__`) |
| `summary()` | Reports R-hat convergence statistics |
| `diagnose()` | Comprehensive diagnostic information |

## HMC Tuning Parameters (Properties)

```python
fit.step_size          # Adapted step size per chain
fit.metric_type        # Metric type (e.g., 'diag_e')
fit.inv_metric         # Inverse metric values
```

## Convergence Diagnostics (Properties)

```python
fit.divergences        # Count of divergent transitions per chain
fit.max_treedepths     # Iterations hitting max treedepth per chain
```

## CmdStanMCMC Properties

| Property | Description |
|----------|-------------|
| `chain_ids` | Chain identifiers |
| `chains` | Number of chains |
| `column_names` | Column names |
| `divergences` | Divergent transitions per chain |
| `inv_metric` | Inverse metric values |
| `max_treedepths` | Max treedepth hits per chain |
| `metadata` | Metadata object |
| `metric` | Metric values |
| `metric_type` | Type of metric |
| `num_draws_sampling` | Number of sampling draws |
| `num_draws_warmup` | Number of warmup draws |
| `step_size` | Adapted step size per chain |
| `thin` | Thinning interval |
| `time` | Timing information |

## Metadata Access

```python
fit.metadata.method_vars    # Sample method variables
fit.metadata.stan_vars      # Stan model variables
```

## Output Management

```python
fit.save_csvfiles(dir='output_directory')  # Move CSV files to specified location
```

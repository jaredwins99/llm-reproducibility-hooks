# CmdStanPy Variational Inference (ADVI)

## Overview

Variational inference is a method for approximating complex Bayesian posterior distributions using simpler, parameterized distributions.

The ADVI algorithm:
- Uses stochastic gradient ascent to approximate the evidence lower bound (ELBO)
- Employs adaptive stepsize sequences with parameter `eta`
- Uses `elbo_samples` draws to approximate the objective function
- Monitors rolling window averages of ELBO change against `tol_rel_obj` threshold for convergence detection

## CmdStanModel.variational()

```python
vb = model.variational(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    seed: Optional[int] = None,
    inits: Optional[float] = None,
    output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    save_latent_dynamics: bool = False,
    save_profile: bool = False,
    algorithm: Optional[str] = None,
    iter: Optional[int] = None,
    grad_samples: Optional[int] = None,
    elbo_samples: Optional[int] = None,
    eta: Optional[float] = None,
    adapt_engaged: bool = True,
    adapt_iter: Optional[int] = None,
    tol_rel_obj: Optional[float] = None,
    eval_elbo: Optional[int] = None,
    draws: Optional[int] = None,
    require_converged: bool = True,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    output_samples: Optional[int] = None,
)
```

**Returns:** `CmdStanVB`

## CmdStanVB Properties

| Property | Description |
|----------|-------------|
| `column_names` | Parameter column identifiers |
| `columns` | Column count |
| `eta` | Step size scaling parameter |
| `metadata` | Metadata object |
| `variational_params_dict` | Inferred means as dictionary |
| `variational_params_np` | Inferred means as numpy array |
| `variational_params_pd` | Inferred means as pandas DataFrame |
| `variational_sample` | Approximate posterior draws (numpy array) |
| `variational_sample_pd` | Approximate posterior draws (pandas DataFrame) |

## CmdStanVB Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values from variational fit |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

## Basic Usage

```python
import os
from cmdstanpy import CmdStanModel, cmdstan_path

bernoulli_dir = os.path.join(cmdstan_path(), 'examples', 'bernoulli')
stan_file = os.path.join(bernoulli_dir, 'bernoulli.stan')
data_file = os.path.join(bernoulli_dir, 'bernoulli.data.json')

model = CmdStanModel(stan_file=stan_file)
vb = model.variational(data=data_file)

print(vb.variational_params_dict)
print(vb.variational_params_pd)
```

## Convergence Handling

By default, the method raises `RuntimeError` if convergence fails. Set `require_converged=False` to inspect non-converged output for diagnostic purposes:

```python
vb = model.variational(data=data_file, require_converged=False)
```

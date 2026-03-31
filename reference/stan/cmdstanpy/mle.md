# CmdStanPy Maximum Likelihood Estimation

## Overview

Stan provides optimization algorithms which find modes of the density specified by a Stan program. Three algorithms are available:

1. **Newton optimizer**
2. **BFGS**
3. **L-BFGS** (the default)

## CmdStanModel.optimize()

```python
mle = model.optimize(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    seed: Optional[int] = None,
    inits: Optional[Union[Mapping, float, str, PathLike]] = None,
    output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    save_profile: bool = False,
    algorithm: Optional[str] = None,
    init_alpha: Optional[float] = None,
    tol_obj: Optional[float] = None,
    tol_rel_obj: Optional[float] = None,
    tol_grad: Optional[float] = None,
    tol_rel_grad: Optional[float] = None,
    tol_param: Optional[float] = None,
    history_size: Optional[int] = None,
    iter: Optional[int] = None,
    save_iterations: bool = False,
    require_converged: bool = True,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    jacobian: bool = False,
)
```

**Returns:** `CmdStanMLE`

## CmdStanMLE Properties

| Property | Description |
|----------|-------------|
| `column_names` | Column names of output |
| `metadata` | Metadata object |
| `optimized_iterations_np` | All iterations as numpy array (if `save_iterations=True`) |
| `optimized_iterations_pd` | All iterations as pandas DataFrame (if `save_iterations=True`) |
| `optimized_params_dict` | Optimized parameter values as dict |
| `optimized_params_np` | Optimized parameter values as numpy array |
| `optimized_params_pd` | Optimized parameter values as pandas DataFrame |

## CmdStanMLE Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values from optimized parameters |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

## Code Example

```python
import os
from cmdstanpy import CmdStanModel, cmdstan_path

bernoulli_dir = os.path.join(cmdstan_path(), 'examples', 'bernoulli')
stan_file = os.path.join(bernoulli_dir, 'bernoulli.stan')
data_file = os.path.join(bernoulli_dir, 'bernoulli.data.json')

model = CmdStanModel(stan_file=stan_file)
mle = model.optimize(data=data_file)

print(mle.column_names)
print(mle.optimized_params_dict)
mle.optimized_params_pd
```

## Results

The output contains parameter estimates including `lp__` (log probability) and model-specific parameters (e.g., `theta` for the Bernoulli model).

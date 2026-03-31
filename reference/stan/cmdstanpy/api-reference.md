# CmdStanPy 1.3.0 API Reference

## CmdStanModel

The primary class that encapsulates a Stan program.

### Constructor

```python
CmdStanModel(
    model_name: Optional[str] = None,
    stan_file: Optional[Union[str, PathLike]] = None,
    exe_file: Optional[Union[str, PathLike]] = None,
    force_compile: bool = False,
    stanc_options: Optional[dict[str, Any]] = None,
    cpp_options: Optional[dict[str, Any]] = None,
    user_header: Optional[Union[str, PathLike]] = None,
    compile: Optional[Union[bool, Literal['force']]] = None,
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `cpp_options` | `dict[str, Union[bool, int]]` | Options to C++ compilers |
| `exe_file` | `Optional[Union[str, PathLike]]` | Full path to Stan exe file |
| `name` | `str` | Model name used in output filename templates |
| `stan_file` | `Optional[Union[str, PathLike]]` | Full path to Stan program file |
| `stanc_options` | `dict[str, Union[bool, int, str]]` | Options to stanc compilers |
| `user_header` | `str` | The user header file if it exists, otherwise empty |

### Methods

#### code()

```python
code() -> Optional[str]
```

Returns the Stan program code.

#### compile()

```python
compile(
    force: bool = False,
    stanc_options: Optional[dict] = None,
    cpp_options: Optional[dict] = None,
    user_header: Optional[Union[str, PathLike]] = None,
    override_options: bool = False,
    _internal: bool = False,
) -> None
```

Translates Stan code to C++ and compiles the executable.

#### diagnose()

```python
diagnose(
    inits: Optional[Union[dict, str, PathLike]] = None,
    data: Optional[Union[Mapping, str, PathLike]] = None,
    epsilon: Optional[float] = None,
    error: Optional[float] = None,
    require_gradients_ok: bool = True,
    sig_figs: Optional[int] = None,
) -> DataFrame
```

Calculates and compares autodiff vs. finite difference gradients.

#### exe_info()

```python
exe_info() -> dict[str, str]
```

Returns executable information.

#### format()

```python
format(
    overwrite_file: bool = False,
    canonicalize: Union[bool, str, Iterable[str]] = False,
    max_line_length: int = 78,
    backup: bool = True,
) -> None
```

Formats the Stan program file.

#### generate_quantities()

```python
generate_quantities(
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
) -> CmdStanGQ[Fit]
```

Produces additional quantities based on existing samples.

#### laplace_sample()

```python
laplace_sample(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    mode: Optional[Union[CmdStanMLE, str, PathLike]] = None,
    draws: Optional[int] = None,
    jacobian: bool = True,
    seed: Optional[int] = None,
    output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    save_profile: bool = False,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    opt_args: Optional[dict[str, Any]] = None,
) -> CmdStanLaplace
```

Draws from Laplace approximation at posterior mode.

#### log_prob()

```python
log_prob(
    params: Union[dict[str, Any], str, PathLike],
    data: Optional[Union[Mapping, str, PathLike]] = None,
    jacobian: bool = True,
    sig_figs: Optional[int] = None,
) -> DataFrame
```

Evaluates log probability and gradient at parameter values.

#### optimize()

```python
optimize(
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
) -> CmdStanMLE
```

Produces penalized maximum likelihood or MAP estimates.

#### pathfinder()

```python
pathfinder(
    data: Optional[Union[Mapping, str, PathLike]] = None,
    init_alpha: Optional[float] = None,
    tol_obj: Optional[float] = None,
    tol_rel_obj: Optional[float] = None,
    tol_grad: Optional[float] = None,
    tol_rel_grad: Optional[float] = None,
    tol_param: Optional[float] = None,
    history_size: Optional[int] = None,
    num_paths: Optional[int] = None,
    max_lbfgs_iters: Optional[int] = None,
    draws: Optional[int] = None,
    num_single_draws: Optional[int] = None,
    num_elbo_draws: Optional[int] = None,
    psis_resample: bool = True,
    calculate_lp: bool = True,
    seed: Optional[int] = None,
    inits: Optional[Union[dict, float, str, PathLike]] = None,
    output_dir: Optional[Union[str, PathLike]] = None,
    sig_figs: Optional[int] = None,
    save_profile: bool = False,
    show_console: bool = False,
    refresh: Optional[int] = None,
    time_fmt: str = '%Y%m%d%H%M%S',
    timeout: Optional[float] = None,
    num_threads: Optional[int] = None,
) -> CmdStanPathfinder
```

Executes Pathfinder variational inference algorithm.

#### sample()

```python
sample(
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
) -> CmdStanMCMC
```

Runs HMC-NUTS sampler for posterior draws.

#### src_info()

```python
src_info() -> dict[str, Any]
```

Returns Stan source file information.

#### variational()

```python
variational(
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
) -> CmdStanVB
```

Implements automatic differentiation variational inference (ADVI).

---

## CmdStanMCMC

Container for sampler outputs created by `sample()`.

### Constructor

```python
CmdStanMCMC(runset: RunSet)
```

### Properties

| Property | Description |
|----------|-------------|
| `chain_ids` | Chain identifiers |
| `chains` | Number of chains |
| `column_names` | Column names |
| `divergences` | Count of divergent transitions per chain |
| `inv_metric` | Inverse metric values |
| `max_treedepths` | Iterations hitting max treedepth per chain |
| `metadata` | Metadata object |
| `metric` | Metric values |
| `metric_type` | Type of metric (e.g., `'diag_e'`) |
| `num_draws_sampling` | Number of sampling draws |
| `num_draws_warmup` | Number of warmup draws |
| `step_size` | Adapted step size per chain |
| `thin` | Thinning interval |
| `time` | Timing information |

### Methods

| Method | Description |
|--------|-------------|
| `create_inits(seed=None, chains=4)` | Generate initial values from existing samples. Returns `Union[list[dict[str, ndarray]], dict[str, ndarray]]` |
| `diagnose()` | Chain diagnostics |
| `draws()` | Access posterior samples as 3-D numpy array |
| `draws_pd()` | Access posterior samples as pandas DataFrame |
| `draws_xr()` | Access posterior samples as xarray Dataset |
| `method_variables()` | Returns dict with sampler diagnostics |
| `save_csvfiles()` | Move CSV files to specified location |
| `stan_variable(name)` | Returns numpy.ndarray for specific variable |
| `stan_variables()` | Returns dict of all Stan variables |
| `summary()` | Statistical summaries with R-hat convergence |

---

## CmdStanMLE

Container for optimization outputs created by `optimize()`.

### Properties

| Property | Description |
|----------|-------------|
| `column_names` | Column names |
| `metadata` | Metadata object |
| `optimized_iterations_np` | All iterations as numpy array (if `save_iterations=True`) |
| `optimized_iterations_pd` | All iterations as pandas DataFrame (if `save_iterations=True`) |
| `optimized_params_dict` | Optimized parameter values as dict |
| `optimized_params_np` | Optimized parameter values as numpy array |
| `optimized_params_pd` | Optimized parameter values as pandas DataFrame |

### Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values from optimized parameters |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

---

## CmdStanLaplace

Container for Laplace approximation outputs created by `laplace_sample()`.

### Properties

| Property | Description |
|----------|-------------|
| `column_names` | Column names |
| `metadata` | Metadata object |
| `mode` | Mode of the Laplace approximation |

### Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values |
| `draws()` | Access draws |
| `draws_xr()` | Access draws as xarray Dataset |
| `method_variables()` | Access method variables |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

---

## CmdStanPathfinder

Container for Pathfinder outputs created by `pathfinder()`.

### Properties

| Property | Description |
|----------|-------------|
| `column_names` | Column names |
| `is_resampled` | Whether PSIS resampling was applied |
| `metadata` | Metadata object |

### Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values |
| `draws()` | Access draws |
| `method_variables()` | Access method variables |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

---

## CmdStanVB

Container for variational inference outputs created by `variational()`.

### Properties

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

### Methods

| Method | Description |
|--------|-------------|
| `create_inits()` | Create initial values from variational fit |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

---

## CmdStanGQ

Container for generated quantities outputs created by `generate_quantities()`.

### Properties

| Property | Description |
|----------|-------------|
| `chain_ids` | Chain identifiers |
| `chains` | Number of chains |
| `column_names` | Column names |
| `metadata` | Metadata object |

### Methods

| Method | Description |
|--------|-------------|
| `draws()` | Returns array of generated quantity draws |
| `draws_pd(inc_sample=True)` | Returns pandas DataFrame combining input drawset with generated quantities |
| `draws_xr()` | Returns xarray Dataset |
| `save_csvfiles()` | Save CSV output files |
| `stan_variable()` | Access a specific Stan variable |
| `stan_variables()` | Access all Stan variables |

---

## Utility Functions

| Function | Description |
|----------|-------------|
| `compile_stan_file()` | Standalone Stan program compilation |
| `format_stan_file()` | Stan program code formatting |
| `show_versions()` | Display CmdStanPy and CmdStan version information |
| `cmdstan_path()` | Get current CmdStan installation path |
| `set_cmdstan_path()` | Set CmdStan installation path |
| `cmdstan_version()` | Get CmdStan version string |
| `install_cmdstan()` | Install CmdStan |
| `rebuild_cmdstan()` | Rebuild CmdStan from source |
| `set_make_env()` | Set Make environment variables |
| `from_csv()` | Load CmdStan output from CSV files |
| `write_stan_json()` | Serialize data to Stan-compatible JSON format |
| `enable_logging()` | Enable diagnostic logging |
| `disable_logging()` | Disable diagnostic logging |

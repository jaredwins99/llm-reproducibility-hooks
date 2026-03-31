# MCMC Sampling using Hamiltonian Monte Carlo - Complete Content

## Overview

The `sample` method enables Bayesian inference using Hamiltonian Monte Carlo (HMC) sampling. The default inference engine is the No-U-Turn Sampler (NUTS), an adaptive form of HMC.

## Running the Sampler

Execute sampling with:

```bash
# Linux/Mac
./bernoulli sample data file=bernoulli.data.json

# Windows
bernoulli.exe sample data file=bernoulli.data.json
```

View all configuration options:
```bash
sample help-all
```

## Stan CSV Output File

Each execution produces a comma-separated value (CSV) file containing:

- **Configuration comments** (lines beginning with `#`)
- **CSV header** with column names
- **Warmup draws** (if `save_warmup=true`)
- **Adaptation results** (step size and inverse mass matrix)
- **Posterior draws**
- **Timing information**

### Standard CSV Columns

HMC sampler information columns:
- `lp__` - total log probability density
- `accept_stat__` - average Metropolis acceptance probability
- `stepsize__` - integrator step size
- `treedepth__` - depth of NUTS tree
- `n_leapfrog__` - number of leapfrog calculations
- `divergent__` - trajectory divergence flag (1 or 0)
- `energy__` - Hamiltonian value
- `int_time__` - total integration time (static HMC only)

## Iterations Configuration

Control iteration count with:

- `num_samples` - number of sampling iterations (default: 1000)
- `num_warmup` - number of warmup iterations (default: 1000)
- `save_warmup` - save warmup draws to output (default: false)
- `thin` - save every Nth iteration (default: 1)

### Iteration Details

"At every sampler iteration, the sampler returns a set of estimates for all
parameters and quantities of interest in the model."

Warmup iterations allow NUTS to adjust the metric and stepsize for efficient typical set sampling. Both `num_samples` and `num_warmup` must be non-negative integers.

**Effective sample size (EFF)** guidance: minimum 100 required for viable estimates. Precision scales as sqrt(N), so each additional decimal place requires 10x more samples.

### Thinning

When `thin=N`, every Nth iteration is saved. Formula for output iterations: `ceiling(M/N)` where M is sampling iterations.

"HMC is not nearly as susceptible to autocorrelation problems and thus
thinning is generally not required nor advised, as HMC can produce
anticorrelated draws."

## Adaptation Configuration

Control adaptation with the `adapt` keyword. Disable all adaptation:
```bash
adapt engaged=false
```

### Step Size Optimization Parameters

- `delta` - target Metropolis acceptance rate (default: 0.8, range: 0-1)
  - Increase to force smaller step sizes
  - Recommend raising to 0.9 or 0.95 for difficult geometries
  - Values above 0.95 indicate poor model geometry

- `gamma` - adaptation regularization scale (default: 0.05, must be positive)
- `kappa` - adaptation relaxation exponent (default: 0.75, must be positive)
- `t_0` - adaptation iteration offset (default: 10, must be positive)

"We recommend always using the default value" for gamma, kappa, and t_0.

### Warmup Schedule Configuration

Configure with positive integers:

- `init_buffer` - iterations tuning step size at adaptation start
- `window` - initial iterations for metric tuning (doubled successively)
- `term_buffer` - iterations to re-tune step size after metric tuning

Values may be adjusted to align with total warmup iterations.

**Warmup Epochs:**
- Stage I (init_buffer): initial fast adaptation
- Stage II (window): expanding slow adaptation intervals
- Stage III (term_buffer): final fast adaptation

### Saving Adapted Metric

Stan 2.34+: use `save_metric=true` to output adapted stepsize and metric as JSON. Output filename: original basename + `_metric.json` suffix (e.g., `output_metric.json` for default `output.csv`).

The saved metric can be reused in subsequent runs via `metric_file`.

## Algorithm Configuration

Use the `algorithm` keyword with values:

- `hmc` - HMC-driven Markov chain (default)
- `fixed_param` - generate samples without changing Markov chain state

### Fixed Parameter Sampling

Required for models with no parameters. Generates pseudo-data via RNG functions in transformed data and generated quantities blocks. Usage:
```bash
algorithm=fixed_param
```

### HMC Samplers

All HMC algorithms require: step size, metric, and integration time.

#### Step Size Parameters

- `stepsize` - distance per Hamiltonian evolution step (default: 1, must be positive)
- `stepsize_jitter` - random jitter range (default: 0, range: 0-1)
  - Value of 1 selects steps from 0 to twice adapted step size
  - Generally recommend keeping default value

#### Metric Options

Specifies the mass matrix type:

- `metric=unit` - unit metric (diagonal ones)
- `metric=diag_e` - diagonal metric (default)
- `metric=dense_e` - dense symmetric positive definite matrix

**Metric file initialization:**

```bash
metric_file=<filepath>
```

For `diag_e`: `inv_metric` is a vector of positive values (one per parameter).
For `dense_e`: `inv_metric` is a positive-definite square matrix.

"The metric_file option can be used with and without adaptation enabled."

#### Integration Time - Engine Selection

- `engine=nuts` - No-U-Turn Sampler (default)
  - Dynamically determines optimal integration time
  - Subargument `max_depth` controls tree depth (default: 10)
  - NUTS forms balanced binary tree, doubling leapfrog steps per iteration

- `engine=static` - user-specified integration time
  - Requires `int_time` parameter (default: 2*pi)

**NUTS behavior:**

"The algorithm is iterative; at each iteration the tree depth is increased
by one, doubling the number of leapfrog steps thus effectively doubling the
computation time."

### Increasing Tree Depth

For difficult posterior geometries:
```bash
algorithm=hmc engine=nuts max_depth=15
```

## Sampler Diagnostic File

Output sampler information and gradients:
```bash
diagnostic_file=<filepath>
```

Produces auxiliary CSV with sampler parameters, unconstrained-scale gradients, and log probabilities for all model parameters.

## Running Multiple Chains

"One way to monitor whether a chain has approximately converged to the
equilibrium distribution is to compare its behavior to other randomly
initialized chains. For robust diagnostics, we recommend running 4 chains."

### Using num_chains Argument

The `num_chains` argument runs multiple chains from a single executable, conserving memory:

```bash
./bernoulli sample num_chains=3 data file=bernoulli.data.json output file=output_1.csv,output_2.csv,output_3.csv
```

Supports comma-separated lists for filename arguments (e.g., `output file=`, `init=`).

**Parallel execution** (with `STAN_THREADS=true` compilation):
```bash
./bernoulli sample num_chains=4 data file=bernoulli.data.json num_threads=4
```

With within-chain parallelization (`map_rect` or `reduce_sum`):
```bash
./bernoulli_par sample num_chains=4 data file=bernoulli.data.json num_threads=16
```

"The threads are automatically scheduled to run the parallel parts of a single
chain or run the sequential parts of another chains."

### Legacy Filename Behavior

When `num_chains > 1` without comma-separated lists, filenames act as templates:

```bash
output file=foo.csv
# Produces: foo_1.csv, foo_2.csv (with num_chains=2)
```

With `id=5` and `num_chains=2`: produces `foo_5.csv`, `foo_6.csv`

For initialization files with `num_chains=3` and `init=bar.json`:
- First checks for `bar_1.json`
- Falls back to `bar.json` if not found

## Summarizing Output with stansummary

Process output files:
```bash
# Linux/Mac
<cmdstan-home>/bin/stansummary output_*.csv

# Windows
<cmdstan-home>\bin\stansummary.exe output_*.csv
```

Reports per-column statistics: mean, standard deviation, percentiles, effective sample size (ESS_bulk, ESS_tail), and R-hat values.

## Example Commands

### Running with Specified RNG Seed

```bash
./my_model sample data file=my_model.data.json \
            output file=output_${i}.csv \
            random seed=12345 id=${i}
```

### Changing Warmup and Sampling Iterations

```bash
./my_model sample num_warmup=500 num_samples=500 \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

### Saving Warmup Draws

```bash
./my_model sample num_warmup=500 num_samples=500 save_warmup=true \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

### Parameter Initialization

```bash
./my_model sample init=my_param_inits.json data file=my_model.data.json \
            output file=output_${i}.csv
```

JSON initialization format example:
```json
{ "theta" : 0.5 }
```

Verify initialization with `fixed_param`:
```bash
./bernoulli sample algorithm=fixed_param num_warmup=0 num_samples=1 \
            init=bernoulli.init.json data file=bernoulli.data.json
```

### Specifying Metric and Stepsize

With default metric value in `bernoulli.diag_e.json`:
```json
{ "inv_metric" : [0.296291] }
```

Usage:
```bash
../my_model sample algorithm=hmc metric_file=bernoulli.diag_e.json \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

With adaptation disabled:
```bash
../my_model sample adapt engaged=false \
            algorithm=hmc stepsize=0.9 \
            metric_file=bernoulli.diag_e.json \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

As of Stan 2.34, save and reuse adapted metrics. Requires specifying both `stepsize` and `metric_file`:
```bash
sample adapt save_metric=true
```

### Changing NUTS-HMC Adaptation Parameters

Increase delta for difficult geometries:
```bash
./my_model sample adapt delta=0.95 \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

Disable adaptation entirely:
```bash
../my_model sample adapt engaged=false \
            algorithm=hmc stepsize=0.9 \
            metric_file=bernoulli.diag_e.json \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

Skip warmup (requires both arguments):
```bash
../my_model sample num_warmup=0 adapt engaged=false \
            algorithm=hmc stepsize=0.9 \
            metric_file=bernoulli.diag_e.json \
            data file=my_model.data.json \
            output file=output_${i}.csv
```

"Even with adaptation disabled, it is still advisable to run warmup iterations
in order to allow the initial parameter values to be adjusted to estimates
which fall within the typical set."

### Capturing Diagnostics and Gradients

```bash
./my_model sample data file=my_model.data.json \
            output file=output_${i}.csv \
            diagnostic_file=diagnostics_${i}.csv
```

### Suppressing Progress Updates

Use `refresh=<int>` to control iteration message frequency (default: 100):

```bash
./my_model sample data file=my_model.data.json \
            output file=output_${i}.csv \
            refresh=0
```

Setting `refresh=0` suppresses iteration messages but retains configuration and timing information.

### Comprehensive Example

```bash
./my_model sample num_warmup=2000 \
           init=my_param_inits.json \
           adapt delta=0.95 init_buffer=100 \
           window=50 term_buffer=100 \
           algorithm=hmc engine=nuts max_depth=15 \
           metric=dense_e metric_file=my_metric.json \
           stepsize=0.6555 \
           data file=my_model.data.json \
           output file=output_${i}.csv refresh=10 \
           random seed=12345 id=${i}
```

Alternative ordering (top-level groups are freely orderable):
```bash
./my_model random seed=12345 id=${i} \
           data file=my_model.data.json \
           output file=output_${i}.csv refresh=10 \
           sample num_warmup=2000 \
           init=my_param_inits.json \
           algorithm=hmc engine=nuts max_depth=15 \
           metric=dense_e metric_file=my_metric.json \
           stepsize=0.6555 \
           adapt delta=0.95 init_buffer=100 \
           window=50 term_buffer=100
```

## Shell Loop Examples (Legacy Parallelism)

### Unix/Linux/Mac - Sequential

```bash
for i in {1..4}
  do
    ./bernoulli sample data file=bernoulli.data.json \
    output file=output_${i}.csv
  done
```

### Unix/Linux/Mac - Parallel

```bash
for i in {1..4}
  do
    ./bernoulli sample data file=bernoulli.data.json \
    output file=output_${i}.csv &
  done
```

### Windows - Sequential

```bash
for /l %i in (1, 1, 4) do start /b bernoulli.exe sample ^
                                    data file=bernoulli.data.json ^
                                    output file=output_%i.csv
```

---

## References

Betancourt, Michael. 2017. "A Conceptual Introduction to Hamiltonian Monte Carlo." *arXiv* 1701.02434. https://arxiv.org/abs/1701.02434.

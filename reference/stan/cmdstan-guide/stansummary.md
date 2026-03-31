# `stansummary`: MCMC Output Analysis

## Overview

The CmdStan `stansummary` program reports statistics for one or more sampler chains over all sampler and model parameters and quantities of interest.

## Statistics Reported

The statistics reported include, in order:

- **Mean** - sample mean
- **MCSE** - Monte Carlo Standard Error, measuring noise in the sample
- **StdDev** - sample standard deviation around the sample mean
- **MAD** - Median Absolute Deviation around the sample median
- **Quantiles** - default 5%, 50%, 95%
- **ESS_bulk**
- **ESS_tail**
- **ESS_bulk/s** - Bulk ESS per second
- **R_hat** - convergence diagnostic statistic

## Key Diagnostic Information

When reviewing output, check the final three columns first as diagnostic statistics. An "R_hat statistic greater than 1 indicates potential convergence problems and that the sample is not representative of the target posterior, thus the estimates of the mean and all other summary statistics are likely to be invalid."

A threshold of 1.01 can be used generically, though other thresholds may apply depending on use case.

## Building `stansummary`

Compile using the makefile:

```bash
cd <cmdstan-home>
make bin/stansummary
```

## Running the Program

**Mac/Linux:**
```bash
<cmdstan-home>/bin/stansummary <file_1.csv> ... <file_N.csv>
```

**Windows:**
```bash
<cmdstan-home>\bin\stansummary.exe <file_1.csv> ... <file_N.csv>
```

### Example Output

```
> bin/stansummary eight_*.csv
Inference for Stan model: eight_schools_model
4 chains: each with iter=1000; warmup=1000; thin=1; 1000 iterations saved.

Warmup took (0.065, 0.078, 0.080, 0.086) seconds, 0.31 seconds total
Sampling took (0.047, 0.044, 0.045, 0.053) seconds, 0.19 seconds total

                 Mean   MCSE  StdDev    MAD       5%   50%   95%  ESS_bulk  ESS_tail  ESS_bulk/s  R_hat

lp__              -19   0.31     4.9    5.0      -27   -19   -11       264       275        1396    1.0
accept_stat__    0.77  0.024    0.31  0.096  6.5e-03  0.93  1.00       243       273        1287    1.0
stepsize__       0.25    nan   0.016  0.016  2.2e-01  0.25  0.26       nan       nan         nan    nan
treedepth__       3.4  0.048    0.76   0.00  2.0e+00   4.0   4.0       285       295        1507    1.0
n_leapfrog__       13   0.80     7.1   0.00  3.0e+00    15    31       220       274        1165    1.0
divergent__     0.015    nan    0.12   0.00  0.0e+00  0.00  0.00       nan       nan         nan    nan
energy__           24   0.32     5.4    5.5  1.5e+01    24    33       289       488        1527    1.0

mu                7.8   0.20     5.5    4.9     -1.3   7.7    17       688       915        3641    1.0
theta[1]           12   0.28     8.7    7.4    -0.36    11    28       908       763        4802    1.0
theta[2]          7.7   0.19     6.8    6.1     -3.4   7.8    19      1194      2011        6320    1.0
theta[3]          5.6   0.23     8.5    7.0     -9.1   6.2    18      1260      1723        6669    1.0
theta[4]          7.5   0.20     7.0    6.5     -4.1   7.6    19      1171      1744        6197    1.0
theta[5]          4.6   0.21     6.7    6.3     -7.0   4.9    15      1045      1513        5530    1.0
theta[6]          5.7   0.23     7.2    6.4     -6.8   6.0    17      1012      1626        5354    1.0
theta[7]           11   0.24     7.1    6.6    0.025    11    24       885       473        4682    1.0
theta[8]          8.4   0.23     8.5    7.3     -4.8   8.1    23      1280      1848        6773    1.0
tau               7.8   0.26     5.9    4.5      1.8   6.3    18       248       178        1310    1.0

Samples were drawn using hmc with nuts.
For each parameter, ESS_bulk and ESS_tail measure the effective sample size for the entire sample (bulk)
and for the .05 and .95 tails (tail), and R_hat measures the potential scale reduction on split chains.
At convergence R_hat will be very close to 1.00.
```

## Sampler Parameters

Initial Stan CSV columns provide information on sampler state:

- **lp__** - total log probability density at each sample
- **accept_stat__** - average Metropolis acceptance probability over each Hamiltonian trajectory
- **stepsize__** - integrator step size
- **treedepth__** - depth of tree used by NUTS
- **n_leapfrog__** - number of leapfrog calculations (NUTS sampler)
- **divergent__** - value 1 if trajectory diverged, otherwise 0 (NUTS sampler)
- **energy__** - value of the Hamiltonian
- **int_time__** - total integration time (static HMC sampler)

## Model Parameters and Quantities of Interest

Remaining columns report parameter values, transformed parameters, and generated quantities in declaration order. For container variables (vectors, matrices, arrays), statistics for each element are reported separately in row-major order.

## Command-Line Options

When invoked with no arguments or with `-h` or `--help`, the program prints usage and exits.

```
Report statistics for one or more Stan CSV files from a HMC sampler run.
Example:  stansummary model_chain_1.csv model_chain_2.csv
Options:
  -a, --autocorr [n]          Display the chain autocorrelation for the n-th
                              input file, in addition to statistics.
  -c, --csv_filename [file]   Write statistics to a CSV file.
  -h, --help                  Produce help message, then exit.
  -p, --percentiles [values]  Percentiles to report as ordered set of
                              comma-separated numbers from (0.1,99.9), inclusive.
                              Default is 5,50,95.
  -s, --sig_figs [n]          Significant figures reported. Default is 2.
                              Must be an integer from (1, 18), inclusive.
  -i, --include_param [name]  Include the named parameter in the summary output.
                              By default, all parameters in the file are summarized,
                              passing this argument one or more times will filter
                              the output down to just the requested arguments.
```

Both short and long option names are allowed. Short names are specified as `-<o> <value>`; long option names can be specified either as `--<option>=<value>` or `--<option> <value>`.

The `--percentiles` argument can be passed an empty string `""`, resulting in no percentiles displayed.

The amount of precision in sampler output limits real precision in the summary report. CmdStan's command line interface has an output argument `sig_figs` with default sampler output precision of 8. The `--sig_figs` argument should not exceed the sampler's `sig_figs` argument.

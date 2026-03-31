# `diagnose`: Diagnosing Biased Hamiltonian Monte Carlo Inferences

## Overview

CmdStan includes a diagnostic utility that analyzes Markov chain output files to identify potential sampling problems:

- Divergent transitions
- Maximum treedepth exceedances
- Low E-BFMI values
- Low effective sample sizes
- High R-hat values

## Building the diagnose Command

Compile the utility using CmdStan's makefile:

```
cd <cmdstan-home>
make bin/diagnose
```

## Running the diagnose Command

Execute diagnose on one or more output files as command-line arguments:

```
bin/diagnose output_*.csv
```

The tool analyzes the files and either confirms satisfactory performance or reports detected issues with remediation suggestions.

## Diagnostic Categories

### Divergent Transitions After Warmup

Divergences indicate the step size cannot resolve features in the posterior distribution. The sampler misses details and produces biased estimates. Solutions include:

- Increasing `adapt_delta` closer to 1
- Reparameterizing the model to simplify posterior geometry
- Addressing hierarchical model structure (e.g., Neal's Funnel example)

### Maximum Treedepth Exceeded

This represents an efficiency concern rather than a validity issue. The No-U-Turn Sampler (NUTS) terminates prematurely when hitting the maximum tree depth cap. Solutions:

- Increase `max_depth` parameter if exceedance frequency remains low

### Low E-BFMI Values

Low Estimated Bayesian Fraction of Missing Information suggests inadequate posterior exploration. Diagnosis involves comparing the standard deviation of the `energy__` column against sqrt(D/2), where D represents unconstrained parameters.

Remediation strategies:

- Run sampler for additional iterations
- Reparameterize to address heavy-tailed posteriors

### Low Effective Sample Sizes

Effective sample size (ESS) captures the information content of dependent MCMC draws. The recommendation requires bulk-ESS greater than 100 times the chain count (e.g., 400 for four chains).

Bulk-ESS reflects sampling efficiency for distribution location estimates (mean, median) using rank-normalized methodology.

### High R-hat Values

The R-hat convergence diagnostic compares between-chain and within-chain estimates. Values exceeding 1.01 indicate incomplete mixing and potentially biased results. Stan reports the maximum of rank-normalized split-R-hat and rank-normalized folded-split-R-hat.

Recommendations:

- Run at least four chains as default practice
- Employ only samples where R-hat < 1.01
- Consider additional prior information or improved parameterization

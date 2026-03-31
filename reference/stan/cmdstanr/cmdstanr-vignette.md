# CmdStanR Getting Started Guide

## Overview
CmdStanR is a lightweight interface to Stan for R users that provides an alternative to the traditional RStan interface.

## Installation

### R Package Installation
```r
install.packages("cmdstanr", repos = c('https://stan-dev.r-universe.dev', getOption("repos")))
library(cmdstanr)
library(posterior)
library(bayesplot)
color_scheme_set("brightblue")
```

### CmdStan Installation Requirements
- C++ toolchain required per: https://mc-stan.org/docs/cmdstan-guide/cmdstan-installation.html
- Verification function: `check_cmdstan_toolchain()`
- Installation function: `install_cmdstan(cores = 2)`

### Path Configuration
Three methods for setting CmdStan path:
1. Environment variable `"CMDSTAN"` at load time
2. Auto-detection from home directory `.cmdstan/cmdstan-[version]` (uses highest version)
3. Manual: `set_cmdstan_path(PATH_TO_CMDSTAN)`

Path verification: `cmdstan_path()` and `cmdstan_version()`

## Model Compilation

```r
file <- file.path(cmdstan_path(), "examples", "bernoulli", "bernoulli.stan")
mod <- cmdstan_model(file)
mod$print()  # Display Stan program
mod$exe_file()  # Get compiled executable path
```

The `cmdstan_model()` function returns an R6 `CmdStanModel` object with methods accessed via `$` operator.

## Running MCMC

```r
data_list <- list(N = 10, y = c(0,1,0,0,0,0,0,0,0,1))

fit <- mod$sample(
  data = data_list,
  seed = 123,
  chains = 4,
  parallel_chains = 4,
  refresh = 500
)
```

The `$sample()` method accepts:
- `data`: named list or path to JSON/R dump file
- `seed`: random seed
- `chains`: number of chains
- `parallel_chains`: parallel execution count
- `refresh`: iteration reporting frequency

Returns `CmdStanMCMC` object with associated methods.

## Posterior Analysis

### Summary Statistics
```r
fit$summary()
fit$summary(variables = c("theta", "lp__"), "mean", "sd")
fit$summary("theta", pr_lt_half = ~ mean(. <= 0.5))
fit$summary(
  variables = NULL,
  posterior::default_summary_measures(),
  extra_quantiles = ~posterior::quantile2(., probs = c(.0275, .975))
)
fit$cmdstan_summary()  # CmdStan's stansummary utility
```

### Posterior Draws
```r
draws_arr <- fit$draws()  # Default: 3-D array (iterations x chains x variables)
draws_df <- fit$draws(format = "df")  # Data frame format
draws_df_2 <- as_draws_df(draws_arr)  # Format conversion
mcmc_hist(fit$draws("theta"))  # bayesplot visualization
```

### Sampler Diagnostics
```r
fit$sampler_diagnostics()  # Default: 3-D array
fit$sampler_diagnostics(format = "df")  # Data frame format
fit$diagnostic_summary()  # Returns: num_divergent, num_max_treedepth, ebfmi
fit$cmdstan_diagnose()  # CmdStan's diagnose utility
```

## Optimization and Variational Methods

### Maximum Likelihood Estimation
```r
fit_mle <- mod$optimize(data = data_list, seed = 123)
fit_mle$print()
fit_mle$mle("theta")
```

### Maximum A Posteriori Estimation
```r
fit_map <- mod$optimize(
  data = data_list,
  jacobian = TRUE,
  seed = 123
)
```

The `jacobian=TRUE` parameter includes Jacobian adjustment for constrained variables.

### Laplace Approximation
```r
fit_laplace <- mod$laplace(
  mode = fit_map,
  draws = 4000,
  data = data_list,
  seed = 123,
  refresh = 1000
)
fit_laplace$print("theta")
```

### Variational Inference (ADVI)
```r
fit_vb <- mod$variational(
  data = data_list,
  seed = 123,
  draws = 4000
)
fit_vb$print("theta")
```

### Pathfinder (Stan 2.33+)
```r
fit_pf <- mod$pathfinder(
  data = data_list,
  seed = 123,
  draws = 4000
)
fit_pf$print("theta")
```

Pathfinder is intended to be faster and more stable than ADVI.

## Saving Fitted Models

### Standard Method
```r
fit$save_object(file = "fit.RDS")
fit2 <- readRDS("fit.RDS")
```

### Faster Method (Large Objects)
```r
fit$draws()
try(fit$sampler_diagnostics(), silent = TRUE)
try(fit$init(), silent = TRUE)
try(fit$profiles(), silent = TRUE)
qs::qsave(x = fit, file = "fit.qs")
fit2 <- qs::qread("fit.qs")
```

### Minimal Storage
```r
fit$draws()
qs::qsave(x = fit, file = "fit.qs")
fit2 <- qs::qread("fit.qs")
```

## CmdStanR vs RStan Comparison

### RStan Advantages
- Supports pre-compiled Stan programs on CRAN (e.g., rstanarm)
- Avoids R6 classes for more familiar syntax
- CRAN binaries available for Mac and Windows

### CmdStanR Advantages
- Compatible with latest versions of Stan. Keeping up with Stan releases is complicated for RStan
- Running Stan via external processes results in fewer unexpected crashes, especially in RStudio
- Less memory overhead
- BSD-3 license (vs GPL-3 for RStan)

## Key Architectural Differences

RStan uses an in-memory interface to Stan and relies on R packages like Rcpp and inline to call C++ code from R. CmdStanR does not directly call any C++ code from R, instead relying on the CmdStan interface behind the scenes.

## Additional Resources
- Vignettes: https://mc-stan.org/cmdstanr/articles/index.html
- Forum: https://discourse.mc-stan.org/
- GitHub Issues: https://github.com/stan-dev/cmdstanr/issues

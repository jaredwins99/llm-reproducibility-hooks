# Working with Posteriors in CmdStanR

## Summary Statistics

The `$summary()` method generates customizable posterior summaries. Default measures include `"mean"`, `"median"`, `"sd"`, `"mad"`, and `"quantile2"`.

### Basic usage
```r
fit$summary()
fit$summary(variables = c("mu", "tau"))
fit$summary(variables = c("mu", "tau"), mean, sd)
```

### Custom summary functions
Can be specified by character string, function, or formula:
```r
fit$summary(
  c("mu", "tau"),
  MEAN = mean,
  "median",
  my_sd,
  ~quantile(.x, probs = c(0.1, 0.9)),
  Minimum = function(x) min(x)
)
```

### Function arguments via .args
```r
fit$summary(c("mu", "tau"), quantile, .args = list(probs = c(0.025, .05, .95, .975)))
```

Summary functions receive arrays with dimensions `iter_sampling x chains`. For variance calculations, use `posterior::variance()` rather than `stats::var()` to avoid returning covariance matrices.

Non-numeric functions work with `$summary()` but not `$print()`.

## Extracting Posterior Draws

The `$draws()` method extracts samples in formats from the **posterior** package.

### Default format (3-D array)
```r
draws_arr <- fit$draws()  # iterations x chains x variables
```

### Data frame format
```r
draws_df <- fit$draws(format = "df")  # draws x variables
```

Convert between formats using `posterior::as_draws_*()` functions.

## Structured Draws (rvar format)

The `rvar` format provides sample-based random variable representation, comparable to `rstan::extract()` output:

```r
draws <- posterior::as_draws_rvars(fit$draws())
x_rvar <- draws$x  # operates like structured matrix
x_array <- posterior::draws_of(draws$x)  # direct array access
```

For a parameter `matrix[2,3] x`, `x_array` yields a `4000 x 2 x 3` array (assuming 4000 draws).

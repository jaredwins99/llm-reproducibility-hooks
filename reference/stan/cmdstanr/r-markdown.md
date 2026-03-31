# R Markdown CmdStan Engine

## Overview

The cmdstanr package provides knitr language engines that enable users to write Stan programs directly within R Markdown documents. Three implementation options exist for processing Stan chunks.

## Option 1: RStan (Default)

The default behavior uses RStan for all Stan chunks:

````markdown
```{stan, output.var="model"}
// Stan model code
```

```{r}
rstan::sampling(model)
```
````

This produces a `stanmodel` object assigned to the variable specified by `output.var`.

## Option 2: CmdStanR for All Chunks

Register the CmdStanR engine with override enabled:

```r
library(cmdstanr)
register_knitr_engine(override = TRUE)
```

This replaces knitr's built-in engine, causing all `stan` chunks to use CmdStanR, producing `CmdStanModel` objects:

````markdown
```{stan, output.var="model"}
// Stan model code
```

```{r}
model$sample()
```
````

## Option 3: Mixed RStan and CmdStanR

Register with `override = FALSE` to use both engines:

```r
register_knitr_engine(override = FALSE)
```

This creates separate `stan` chunks (RStan) and `cmdstan` chunks (CmdStanR).

## Additional Features

### Caching
Use `cache=TRUE` chunk option to prevent recompilation during knitting.

### Interactive Use
When running chunks interactively in RStudio, use `override = FALSE` and convert `stan` chunks to `cmdstan` chunks as a workaround.

# Example Model and Data

## Overview

This page demonstrates a basic Stan program for Bernoulli modeling with binary outcome data. The example shows both the model code and corresponding data format.

## Stan Model Code

```stan
data {
  int<lower=0> N;
  array[N] int<lower=0, upper=1> y;
}
parameters {
  real<lower=0, upper=1> theta;
}
model {
  theta ~ beta(1, 1);  // uniform prior on interval 0,1
  y ~ bernoulli(theta);
}
```

## Model Description

The program implements a Bernoulli model where "binary observed data `y[1],...,y[N]` are i.i.d. with Bernoulli chance-of-success `theta`."

## Data Format Example

The data block requires two variables: `N` and `y`. An example dataset with N=10 observations (8 failures, 2 successes) appears in both JSON and Rdump formats.

### JSON Format

```json
{
    "N" : 10,
    "y" : [0,1,0,0,0,0,0,0,0,1]
}
```

## References

The model is located at `<cmdstan-home>/examples/bernoulli/bernoulli.stan` within the CmdStan distribution.

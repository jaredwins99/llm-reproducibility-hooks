# Stan Parallelization Guide

## Overview

Stan provides three parallelization mechanisms: multi-threading via Intel Threading Building Blocks (TBB), multi-processing through Message Passing Interface (MPI), and GPU computing with OpenCL.

## Reduce-Sum Approach

The `reduce_sum` function parallelizes calculations where you need to compute sums of independent function evaluations—common in log-likelihood computations.

**Key advantage**: "More flexible argument interface, avoiding the packing and unpacking that is necessary with rectangular map."

### Function Signatures

```stan
real reduce_sum(F f, array[] T x, int grainsize, T1 s1, T2 s2, ...)
real reduce_sum_static(F f, array[] T x, int grainsize, T1 s1, T2 s2, ...)
```

User-defined partial sum functions must have:
```stan
real f(array[] T x_slice, int start, int end, T1 s1, T2 s2, ...)
```

### Logistic Regression Example

A basic model vectorizing likelihood calculations:

```stan
functions {
  real partial_sum(array[] int y_slice,
                   int start, int end,
                   vector x,
                   vector beta) {
    return bernoulli_logit_lpmf(y_slice |
           beta[1] + beta[2] * x[start:end]);
  }
}
data {
  int N;
  array[N] int y;
  vector[N] x;
}
parameters {
  vector[2] beta;
}
model {
  int grainsize = 1;
  beta ~ std_normal();
  target += reduce_sum(partial_sum, y,
                       grainsize, x, beta);
}
```

### Grainsize Selection

The documentation suggests: "start with `grainsize = 2500`" for N=10,000 with 4 cores, then halve repeatedly until performance degrades. Optimal values may be surprisingly small—"even thirty or forty or smaller might be the best."

## Map-Rect Function

Map-reduce breaks computations into modular components. The `map_rect` function applies a function across shards of data.

### Function Signature

```stan
vector map_rect(
  (vector, vector, array[] real, array[] int):vector f,
  vector phi,
  array[] vector thetas,
  data array[,] real x_rs,
  data array[,] int x_is
);
```

The mapped function must have signature:
```stan
vector f(vector phi, vector theta,
         data array[] real x_r,
         data array[] int x_i);
```

### Simple Logistic Regression with Map-Rect

```stan
functions {
  vector lr(vector beta, vector theta,
            array[] real x, array[] int y) {
    real lp = bernoulli_logit_lpmf(y | beta[1]
                                   + to_vector(x) * beta[2]);
    return [lp]';
  }
}
data {
  array[12] int y;
  array[12] real x;
}
transformed data {
  array[3, 4] int ys = { y[1:4], y[5:8], y[9:12] };
  array[3, 4] real xs = { x[1:4], x[5:8], x[9:12] };
  array[3] vector[0] theta;
}
parameters {
  vector[2] beta;
}
model {
  beta ~ std_normal();
  target += sum(map_rect(lr, beta, theta, xs, ys));
}
```

## Key Differences

**Reduce-sum advantages**:
- Automatic data partitioning
- Simpler interface
- Single-machine parallelization only

**Map-rect advantages**:
- Returns vector results (not just scalars)
- Supports distributed computing across multiple machines
- More control over sharding

## OpenCL Support

Stan supports automatic GPU/CPU parallelization for numerous distributions including `bernoulli_lpmf`, `normal_lpdf`, `poisson_lpmf`, and generalized linear model variants. Requires compilation with `STAN_OPENCL` flag and an OpenCL runtime installation.

## Performance Considerations

The documentation notes that "maximal speedup one can achieve is capped" by Amdahl's law—only portions of programs run in parallel, limiting overall gains.

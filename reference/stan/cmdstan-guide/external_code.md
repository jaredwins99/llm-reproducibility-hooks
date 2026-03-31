# Using External C++ Code in Stan

## Overview

Stan allows integration of external C++ code through special compiler flags and header files. This enables users to define functions declared in Stan but implemented in C++.

## Basic Setup

Two makefile variables must be specified:

1. **`STANCFLAGS=--allow-undefined`** - Permits undefined functions in Stan language without parser errors
2. **`USER_HEADER=<header_file.hpp>`** - Specifies the header file containing function definitions

The function can exist in the global namespace or in the model namespace (defined as the model name followed by `_namespace`).

## Example Implementation

For a Bernoulli model declaring an undefined `make_odds` function:

```stan
functions {
  real make_odds(data real theta);
}
```

Create a header file (`make_odds.hpp`):

```cpp
#include <ostream>

double make_odds(const double& theta, std::ostream *pstream__) {
  return theta / (1 - theta);
}
```

Compile with:
```
make STANCFLAGS=--allow-undefined USER_HEADER=examples/bernoulli/make_odds.hpp examples/bernoulli/bernoulli
```

Alternatively, place `STANCFLAGS` and `USER_HEADER` in the `make/local` file.

## Autodifferentiation Support

For functions requiring automatic differentiation, use template syntax:

```cpp
template <typename T>
T make_odds(const T &theta, std::ostream *pstream__)
{
    return theta / (1 - theta);
}
```

## Derivative Specializations

External functions can encode analytic gradients using reverse-mode specialization. Implementation requires:

- `#include <stan/model/model_header.hpp>`
- Prefix Stan Math Library calls with `stan::math::`
- Separate template overloads for autodiff and non-autodiff cases

## Special Function Requirements

Certain function types have specific signature requirements:

**RNGs** (ending in `_rng`):
- Receive a base RNG object as the second-to-last argument
- Currently `stan::rng_t` (alias to `boost::rng::mixmax`)

**Target-editing functions** (ending in `_lp`):
- Receive `lp__` reference and `stan::math::accumulator` object
- Require boolean template parameter `propto__`

**Probability distributions** (ending in `_lpdf` or `_lpmf`):
- Require boolean template parameter `propto__`

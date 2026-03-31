# Stan Math Library

Source: https://mc-stan.org/math/

The Stan Math Library is a BSD-3 licensed C++ reverse-mode automatic differentiation library designed to facilitate the construction and utilization of algorithms that utilize derivatives.

## Required Dependencies

Stan Math requires four specific libraries, distributed in the `lib/` subdirectory. Only these tested versions are officially supported:

- **Boost** (version 1.81.0)
- **Eigen** (version 3.3.9)
- **SUNDIALS** (version 6.1.1)
- **Intel TBB** (version 2020.3)

## Installation Process

The library uses `make` as its build system. A basic example demonstrates computing a normal log probability density:

```cpp
#include <stan/math.hpp>
#include <iostream>

int main() {
  std::cout << "log normal(1 | 2, 3)="
  << stan::math::normal_lpdf(1, 2, 3)
  << std::endl;
}
```

Compilation involves two make commands:

1. `make -j4 -f <path>/stan-math/make/standalone math-libs` (builds dependencies once)
2. `make -f <path>/stan-math/make/standalone foo` (compiles your program)

The standalone makefile automatically provides necessary include paths and library linking. On Windows, users must manually manage the `tbb.dll` file location.

## Intel TBB Configuration

Users can configure external TBB libraries using `TBB_LIB` and `TBB_INC` environment variables. For oneTBB on Linux systems, set the `TBB_INTERFACE_NEW=true` flag in `make/local`.

## Compiler Requirements

The library supports C++11 fully and C++14 partially. The g++ 4.9.3 version (part of RTools for Windows) defines the minimal C++ feature set required by the Stan Math library.

Compilers are specified via the `CXX` variable in a `make/local` configuration file. Compiler changes require cleaning and rebuilding dependencies.

## Licensing

Stan Math uses the new BSD license. The Intel TBB dependency operates under the Apache 2.0 license, which creates potential incompatibility with GPL-2 licensed code when distributed as unified binaries.

## Contributing

The project welcomes contributions through discussions, issues, and pull requests via mc-stan.org/math.

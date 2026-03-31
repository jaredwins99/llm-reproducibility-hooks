# Reproducibility in Stan

## Overview

Stan aims for full reproducibility, though this is limited by floating-point arithmetic constraints. According to the documentation, "Stan results will only be exactly reproducible if _all_ of the following components are _identical_."

## Required Identical Components

For exact reproducibility, these elements must match:

- Stan version
- Stan interface (RStan, PyStan, CmdStan) and language version
- Included library versions (Boost, Eigen)
- Operating system version
- Computer hardware (CPU, motherboard, memory)
- C++ compiler, version, flags, and linked libraries
- Stan configuration (random seed, chain ID, initialization, data)

## Key Limitations

The document emphasizes that compiler optimization flags significantly affect results. Changing from `-O3` to `-O2` or `-O0` can produce different floating-point outputs from identical source code.

Data must match "down to the bit level," and interface libraries like Rcpp can affect reproducibility if they change their conversion processes between R and C++ types.

## Notable Version Changes

**Stan 2.28**: Changed default chain ID for MCMC from `0` to `1`, causing different outputs for users with set seeds but unspecified chain IDs.

**Stan 2.35**: Implemented a new default pseudo-random number generator with no relationship to pre-2.35 seeds.

The document notes these changes represent exceptions; most version transitions offer no reproducibility guarantees.

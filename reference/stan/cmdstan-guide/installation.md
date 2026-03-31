# CmdStan Installation Guide

## Overview

CmdStan can be installed through two primary methods: using the conda package manager (recommended for Windows users) or building from GitHub source code.

## Installation via Conda

### Basic Installation

Create a new conda environment with CmdStan:

```bash
conda create -n stan -c conda-forge cmdstan
```

For existing environments:

```bash
conda install -c conda-forge cmdstan
```

Activate the environment:

```bash
conda activate stan
```

### Version-Specific Installation

To install a specific CmdStan version (2.26.1 or newer):

```bash
conda install -c conda-forge cmdstan=2.27.0
```

### Installation Location

View conda environment locations:

```bash
conda info -e
```

CmdStan installs to `$CONDA_PREFIX/bin/cmdstan` (Linux/MacOS) or `%CONDA_PREFIX%\bin\cmdstan` (Windows).

For conda-specific issues, report to the [conda-forge issue tracker](https://github.com/conda-forge/cmdstan-feedstock/issues).

## Installation from GitHub

### Prerequisites

Verify you have a modern C++ toolchain installed before proceeding.

### Downloading Source Code

Download a release tarfile (not "Source Code" links):

```bash
git clone https://github.com/stan-dev/cmdstan.git --recursive
```

The downloaded directory is referred to as `<cmdstan-home>`.

### Building CmdStan

From the CmdStan home directory:

```bash
cd <cmdstan-home>
make build
```

For parallel builds using 4 cores:

```bash
make -j4 build
```

**Note:** Build process may require 10+ minutes and 2+ GB of memory.

### Windows TBB Library Configuration

Add to PATH:

```
<cmdstan-home>/stan/lib/stan_math/lib/tbb
```

Or run:

```bash
make install-tbb
```

## Verification

### Linux/macOS

```bash
# Compile example
make examples/bernoulli/bernoulli

# Run sampling
./examples/bernoulli/bernoulli sample data file=examples/bernoulli/bernoulli.data.json

# Check output
wc -l output.csv

# Summarize results
bin/stansummary output.csv
```

### Windows

```bash
# Compile example
make examples/bernoulli/bernoulli.exe

# Run sampling
./examples/bernoulli/bernoulli.exe sample data file=examples/bernoulli/bernoulli.data.json

# Summarize results
bin/stansummary.exe output.csv
```

## Troubleshooting

### Clean and Rebuild

```bash
cd <cmdstan-home>
make clean-all
make build
```

### Common Issues

**PCH File Errors:** Clean and rebuild as shown above.

**Windows Tool Not Found:** Ensure C++ toolchain is in PATH.

**Spaces in Paths:** Avoid installing CmdStan or models in paths with spaces.

## C++ Toolchain Requirements

### Linux

Required: `g++` 4.9.3+ and GNU Make 3.81+

Check versions:

```bash
g++ --version
make --version
```

Install/upgrade:

```bash
sudo apt install g++
sudo apt install make
```

### macOS

Check for Xcode tools:

```bash
clang++ --version
make --version
```

Install if missing:

```bash
xcode-select --install
```

### Windows

Check for tools:

```bash
g++ --version
make --version
```

#### RTools45 Installation (Intel/AMD 64-bit)

Download [RTools45 installer](https://github.com/r-hub/rtools45/releases/download/latest/rtools45.exe).

Add to PATH:

```
C:\rtools45\usr\bin
C:\rtools45\x86_64-w64-mingw32.static.posix\bin
```

#### RTools45 Installation (ARM 64-bit)

Download [RTools45-ARM64 installer](https://github.com/r-hub/rtools45/releases/download/latest/rtools45-aarch64.exe).

Add to PATH:

```
C:\rtools45-aarch64\usr\bin
C:\rtools45-aarch64\aarch64-w64-mingw32.static.posix\bin
```

## GNU Make Usage

### Basic Syntax

```bash
make <flags> <variables> <targets>
```

### Setting Variables

Command-line example:

```bash
make STAN_OPENCL=TRUE ../my_dir/my_program
```

Persistent configuration via `<cmdstan-home>/make/local`:

```
STAN_OPENCL=TRUE
```

### Available Make Targets

**Build utilities:**

```bash
make build
```

**Compile Stan program:**

```bash
make foo/bar
```

**Clean build artifacts:**

```bash
make clean-all
```

### Make Variables Reference

Available variables documented in `<cmdstan-home>/cmdstan/stan/lib/stan_math/make/compiler_flags`.

Common variables:
- `STANCFLAGS`: Extra options passed to Stan compiler
- `USER_HEADER`: Header file for undefined functions (default: "user_header.hpp")
- `STANC3_VERSION`: Specify tagged compiler version
- `STAN_CPP_OPTIMS`: Enable additional compiler optimizations
- `STAN_NO_RANGE_CHECKS`: Remove range checks for performance

### CmdStan Tools

Upon successful build, `<cmdstan-home>/bin/` contains:

- `stanc`: Stan language compiler (translates to C++)
- `stansummary`: Posterior analysis utility
- `diagnose`: HMC sampler diagnostic tool

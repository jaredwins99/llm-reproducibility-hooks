# Parallelization in Stan

Stan provides three parallelization approaches for model execution:

## Multi-threading with TBB

**Purpose**: Exploits multi-threading in Stan models

**Requirements**: Models must be rewritten using `reduce_sum` and `map_rect` functions

**Compilation**:
Set the `STAN_THREADS` makefile flag. Recommended approach via `make/local`:

```
STAN_THREADS=true
```

Then compile normally:
```
make path/to/model
```

**Execution**:
Specify maximum threads using the `num_threads` argument (positive integers or -1 for all cores):

```
./model sample data file=data.json num_threads=4 ...
```

For multiple chains with combined thread pool:
```
./model sample num_chains=2 data file=data.json num_threads=8 ...
```

## Multi-processing with MPI

**Purpose**: Parallelization across multiple cores or clusters

**Supported platforms**: macOS and Linux

**Dependencies**: Requires MPI implementation (MPICH or OpenMPI)

**Compilation flags** for `make/local`:
- `STAN_MPI`: Enables MPI support
- `CXX`: MPI C++ compiler wrapper (typically `mpicxx`)
- `TBB_CXX_TYPE`: Wrapped C++ compiler (`gcc` on Linux, `clang` on macOS)

Example Linux configuration:
```
STAN_MPI=true
CXX=mpicxx
TBB_CXX_TYPE=gcc
```

**Execution**:
Use MPI launcher with process count:
```
mpiexec -n 6 path/to/model sample data file=data.json ...
```

## OpenCL

**Support**: Most modern CPUs and GPUs

**Prerequisites**: OpenCL runtime for target device; verify with `clinfo` tool

**GPU Installation**:

*NVIDIA*: Install GPU driver and CUDA Toolkit
```
sudo apt update
sudo apt install nvidia-driver-460 nvidia-cuda-toolkit
```

*AMD*: Install Radeon Software (Linux) or OCL-SDK (Windows)

*Intel*: Follow [Intel's installation instructions](https://software.intel.com/content/www/us/en/develop/articles/opencl-drivers.html)

*AMD CPU*: Install PoCL

**Compilation**:
Set `STAN_OPENCL` flag in `make/local`:
```
STAN_OPENCL=true
```

For integrated GPUs, also add:
```
INTEGRATED_OPENCL=true
```

**Execution**:
Specify platform and device IDs:
```
path/to/model sample data file=data.json opencl platform=0 device=1
```

Default device IDs (0) are used if omitted when single GPU exists.

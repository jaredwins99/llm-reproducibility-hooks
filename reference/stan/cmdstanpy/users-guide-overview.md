# CmdStanPy User's Guide Overview

## Core Functionality

CmdStanPy is a lightweight interface to Stan for Python that enables Bayesian statistical modeling through several key capabilities:

### Inference Methods Available

- **NUTS-HMC sampler** for exact Bayesian estimation
- **Pathfinder and ADVI** for approximate Bayesian estimation
- **Optimization-based MAP** (Maximum A Posteriori) estimation

### Workflow Operations

Users can:
1. Compile Stan models
2. Perform inference conditioned on data
3. Generate new quantities of interest
4. Manage outputs through extraction, summarization, and file storage

## Design Philosophy

The interface wraps CmdStan's file-based command line interface and emphasizes minimal memory overhead beyond what CmdStan itself requires. This can enable fitting of complex models to larger datasets compared to PyStan or RStan implementations.

### File Management

- During **development**, output files default to temporary filesystem storage
- For **production deployment**, users can specify custom output directories for CmdStan results

## Documentation Structure

### Guides

- **Hello, World!** (`hello_world.html`) - Getting started
- **CmdStanPy Workflow** (`workflow.html`) - Standard workflow patterns
- **Controlling Outputs** (`outputs.html`) - Output management

### Examples

- **MCMC Sampling** (`examples/MCMC%20Sampling.html`) - HMC-NUTS posterior sampling
- **Maximum Likelihood Estimation** (`examples/Maximum%20Likelihood%20Estimation.html`) - Optimization-based estimation
- **Pathfinder** (`examples/Pathfinder.html`) - Pathfinder variational inference
- **ADVI** (`examples/Variational%20Inference.html`) - Automatic Differentiation Variational Inference
- **VI as Sampler Initialization** (`examples/VI%20as%20Sampler%20Inits.html`) - Using VI to initialize samplers
- **Generated Quantities** (`examples/Run%20Generated%20Quantities.html`) - Post-hoc quantity generation
- **External C++ Functions** (`examples/Using%20External%20C%2B%2B.html`) - Custom C++ integration

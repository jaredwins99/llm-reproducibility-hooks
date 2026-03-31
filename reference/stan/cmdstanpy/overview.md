# CmdStanPy 1.3.0 Overview

CmdStanPy is a lightweight pure-Python interface to CmdStan which provides access to the Stan compiler and all inference algorithms.

- **Repository**: https://github.com/stan-dev/cmdstanpy
- **Documentation**: https://mc-stan.org/cmdstanpy/
- **Forums**: https://discourse.mc-stan.org/

## Inference Methods

- NUTS-HMC sampler for exact Bayesian estimation
- Pathfinder and ADVI for approximate Bayesian estimation
- Optimization-based MAP (Maximum A Posteriori) estimation

## Design Philosophy

The interface wraps CmdStan's file-based command line interface and emphasizes minimal memory overhead beyond what CmdStan itself requires, potentially enabling fitting of complex models to larger datasets compared to PyStan or RStan implementations.

During development, output files default to temporary filesystem storage. For production deployment, users can specify custom output directories for CmdStan results.

## Key Classes

| Class | Description |
|-------|-------------|
| `CmdStanModel` | Encapsulates a Stan program; provides compilation and all inference methods |
| `CmdStanMCMC` | Container for HMC-NUTS sampler output |
| `CmdStanMLE` | Container for optimization (MLE/MAP) output |
| `CmdStanLaplace` | Container for Laplace approximation output |
| `CmdStanPathfinder` | Container for Pathfinder variational inference output |
| `CmdStanVB` | Container for ADVI variational inference output |
| `CmdStanGQ` | Container for generated quantities output |

## Key Utility Functions

| Function | Description |
|----------|-------------|
| `compile_stan_file()` | Standalone compilation |
| `format_stan_file()` | Code formatting |
| `cmdstan_path()` | Get CmdStan installation path |
| `set_cmdstan_path()` | Set CmdStan installation path |
| `install_cmdstan()` | Install CmdStan |
| `rebuild_cmdstan()` | Rebuild CmdStan |
| `write_stan_json()` | Data serialization to JSON |
| `show_versions()` | Display version information |
| `enable_logging()` / `disable_logging()` | Diagnostic logging control |

## Documentation Sections

- [Installation](installation.md)
- [User's Guide Overview](users-guide-overview.md)
- [MCMC Sampling](mcmc-sampling.md)
- [Maximum Likelihood Estimation](mle.md)
- [Variational Inference (ADVI)](variational-inference.md)
- [Generated Quantities](generated-quantities.md)
- [API Reference](api-reference.md)

## Additional Example Topics

- Hello, World!
- CmdStanPy Workflow
- Controlling Outputs
- Pathfinder (Variational Inference)
- VI as Sampler Initialization
- External C++ Functions

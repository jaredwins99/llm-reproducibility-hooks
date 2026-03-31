# CmdStan Common Issues and Troubleshooting

Source: https://discourse.mc-stan.org/c/interfaces/cmdstan/28

## Installation Issues

### macOS
- **macOS Sequoia/Tahoe compilation failures**: Common issue with newer macOS
  versions. Check Xcode command line tools are installed and up to date.
  - Thread: https://discourse.mc-stan.org/t/cannot-compile-anything-with-cmdstan-macos-tahoa/40676
  - Thread: https://discourse.mc-stan.org/t/install-issues-of-cmdstan-on-macos/39198

### Windows
- **Rtools toolchain issues**: Behind firewalls, install from tarball.
  - Thread: https://discourse.mc-stan.org/t/how-to-install-rtools-4-4-toolchain-for-cmdstanr-on-windows-from-tarball-behind-firewall/38641
- **mingw32-make compilation errors**: Common TBB library build failures.
  - Thread: https://discourse.mc-stan.org/t/cmdstan-mingw32-make-compilation-error-1/38414
- **Models crash instantly on Windows**: Serial or parallel.
  - Thread: https://discourse.mc-stan.org/t/cmdstanr-models-crash-instantly-on-windows-serial-or-parallel/40528

### Linux
- **GLIBC version errors**: Mismatch between system and expected library versions.
  - Thread: https://discourse.mc-stan.org/t/cmdstanr-error-version-glibc-2-32-not-found/39888
- **Apptainer/container issues**: Exec format errors when compiling from source.
  - Thread: https://discourse.mc-stan.org/t/compiling-cmdstan-from-source-in-an-apptainer-container-exec-format-error/39295

## Runtime Issues

### Performance
- **CmdStanR sampling very slow compared to RStan**: Usually caused by different
  default settings or compilation flags.
  - Thread: https://discourse.mc-stan.org/t/cmdstanr-sampling-very-slow-compared-to-rstan/37590
- **Cluster sampling speed**: Considerations for HPC environments.
  - Thread: https://discourse.mc-stan.org/t/cmdstan-cluster-sampling-speed/38443

### Parallelization
- **Parallel chains on Windows**: Known issues with parallel execution.
  - Thread: https://discourse.mc-stan.org/t/help-needed-with-cmdstanr-parallel-chains/40307
- **General parallelization**: Options for within-chain and between-chain.
  - Thread: https://discourse.mc-stan.org/t/parallelization/39110
- **GPU/OpenCL on WSL**: Running Stan on GPU via Windows Subsystem for Linux.
  - Thread: https://discourse.mc-stan.org/t/running-stan-on-the-gpu-with-opencl-on-wsl-seeking-assistance/36149

### C++ Compatibility
- **C++20 issues with CmdStan 2.36+**: Compiler compatibility problems.
  - Thread: https://discourse.mc-stan.org/t/trouble-updating-cmdstan-to-2-36-c-20-compatibility-issues/38309
- **Intel TBB errors**: Thread Building Blocks library compilation issues.
  - Thread: https://discourse.mc-stan.org/t/cmdstan-intel-tbb-error-when-compiling-model/38618

## CmdStanR-Specific

- **Installation on fresh macOS + RStudio**: Step-by-step troubleshooting.
  - Thread: https://discourse.mc-stan.org/t/cannot-install-cmdstanr-on-freshly-installed-macos-rstudio/26736
- **No output issues**: Silent failures during sampling.
  - Thread: https://discourse.mc-stan.org/t/no-output-issue-with-cmdstanr/40370
- **Quarto rendering with CmdStanR**: Integration issues.
  - Thread: https://discourse.mc-stan.org/t/quarto-rendering-library-cmdstanr/39851

## CmdStanPy-Specific

- **Model recompilation failures**: Models recompile unexpectedly on some systems.
  - Thread: https://discourse.mc-stan.org/t/cmdstanpy-recompiles-models-and-fails-on-some-systems/40172
- **ArviZ integration**: Adding coordinates to inference objects.
  - Thread: https://discourse.mc-stan.org/t/adding-coordinates-and-imd-to-arviz-inference-object-after-cmdstanpy/38589

## Multi-User Environments

- **Shared CmdStan installation**: Multiple users can run simultaneously from a
  shared installation without issues, as long as they compile to separate directories.
  - Thread: https://discourse.mc-stan.org/t/would-there-be-any-issue-to-have-multiple-users-run-cmdstan-simultaneously-from-a-shared-installation/39789

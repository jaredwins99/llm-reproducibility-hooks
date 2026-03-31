# CmdStanPy Installation Guide

## Requirements

- Python 3
- Modern C++ toolchain

## Installation Methods

### 1. Conda (Recommended)

Create new environment:
```bash
conda create -n stan -c conda-forge cmdstanpy
```

Install into existing environment:
```bash
conda install -c conda-forge cmdstanpy
```

Activate environment:
```bash
conda activate stan
```

**Version specification:** CmdStan versions 2.26.1 and newer can be installed by specifying `cmdstan==VERSION`.

**Location:** `$CONDA_PREFIX/bin/cmdstan` (Linux/MacOS) or `%CONDA_PREFIX%\bin\cmdstan` (Windows)

### 2. PyPI with pip

```bash
pip install --upgrade cmdstanpy
```

With optional packages (includes `xarray` for output handling):
```bash
pip install --upgrade cmdstanpy[all]
```

### 3. GitHub

```bash
pip install -e git+https://github.com/stan-dev/cmdstanpy@develop#egg=cmdstanpy
```

## C++ Toolchain Requirements

| Platform | Requirements |
|----------|-------------|
| **Linux** | g++ 4.9.3 and GNU-Make |
| **MacOS** | Xcode and command line tools (`xcode-select --install`) |
| **Windows** | RTools 4.0 with g++ 8 compiler |

## Installing CmdStan

### From Python

```python
import cmdstanpy

cmdstanpy.install_cmdstan()
cmdstanpy.install_cmdstan(compiler=True)  # Windows only
```

### From Command Line (Linux/MacOS)

```bash
install_cmdstan
ls -F ~/.cmdstan
```

### From Command Line (Windows)

```bash
install_cmdstan --compiler
dir "%HOME%/.cmdstan"
```

### install_cmdstan Arguments

| Argument | Description |
|----------|-------------|
| `-i` or `--interactive` | Interactive mode with prompts |
| `-d <directory>` | Override install location |
| `-v <version>` | Specify CmdStan version |

**Default location:** `~/.cmdstan`

## Alternate Linux Architectures

Supported architectures: `arm64`, `armel`, `armhf`, `mips64el`, `ppc64el`, `s390x`

Override with `CMDSTAN_ARCH` environment variable.

## Setting CmdStan Path

```python
from cmdstanpy import cmdstan_path, set_cmdstan_path
import os

set_cmdstan_path(os.path.join('path', 'to', 'cmdstan'))
cmdstan_path()
```

The `CMDSTAN` environment variable registers installation location.

## Special Notes

- **PyStan/RTools users:** Install in separate virtual environments to avoid conflicts
- **Jupyter users:** May require `ipywidgets` installation for progress bars

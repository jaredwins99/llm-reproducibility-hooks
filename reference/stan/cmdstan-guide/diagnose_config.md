# Diagnosing HMC by Comparison of Gradients

## Overview

CmdStan offers a diagnostic feature to compare analytically computed gradients with those calculated via finite differences. Discrepancies suggest potential issues with the model, initial states, or Stan itself.

## Configuration Arguments

The `diagnose` method uses a `test` subargument (currently supporting only `gradient`). Two configuration options are available:

- **`epsilon`**: The finite difference step size. Must be positive. Default: 1e-06
- **`error`**: The error threshold. Must be positive. Default: 1e-06

## Usage Examples

### Default Configuration (Mac OS/Linux)
```
./my_model diagnose data file=my_data
```

### Default Configuration (Windows)
```
my_model diagnose data file=my_data
```

### With Custom Error Threshold
```
./my_model diagnose test=gradient error=0.0001 data file=my_data
```

### Example with Bernoulli Model
```
./bernoulli diagnose data file=bernoulli.data.R
```

## Output Example

The console displays:
- Configuration settings (epsilon, error values)
- Log probability value
- Parameter table with columns: index, value, model gradient, finite difference gradient, error

The same information is printed to the CSV output file as comment lines (prefixed with `#`).

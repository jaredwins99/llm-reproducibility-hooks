# Compiling a Stan Program

## Overview

A Stan program must reside in a file with the `.stan` extension. The CmdStan makefile orchestrates a two-stage compilation process:

1. The Stan program is converted to C++ using the `stanc` compiler
2. The C++ compiler compiles all sources and links them with the CmdStan interface, Stan library, and math library

## Invoking the Make Utility

To compile Stan programs, invoke Make from the `<cmdstan-home>` directory. Stan program files can be located elsewhere, but "directory path names cannot contain spaces - this limitation is imposed by Make."

**Mac and Linux syntax:**
```
> cd <cmdstan_home>
> make examples/bernoulli/bernoulli
```

**Windows syntax:**
```
> make examples/bernoulli/bernoulli.exe
```

(Note: Windows requires `.exe` suffix and forward slashes in paths, not backslashes)

The generated files--C++ code (`bernoulli.hpp`), object file (`bernoulli.o`), and executable--are placed in the same directory as the Stan program.

## Dependencies

Make checks dependencies on each invocation. If source files haven't changed, subsequent calls skip recompilation:

```
> make examples/bernoulli/bernoulli
make: `examples/bernoulli/bernoulli' is up to date.
```

Modifying the Stan program triggers a rebuild on the next Make call.

## Compiler Errors

### Syntax and Semantic Errors

Stan's strongly-typed language detects various errors during translation. Examples include:

**Missing identifier:**
```
Semantic error in 'bernoulli.stan', line 9, column 2 to column 7:
   thata ~ beta(1, 1);
Identifier 'thata' not in scope.
```

**Type mismatch:**
```
Semantic error in 'foo.stan', line 5, column 2 to column 12:
   int y = x;
Ill-typed arguments supplied to assignment operator =:
 lhs has type int and rhs has type real
```

Reference the "Stan Reference Manual" and "Stan User's Guide" for comprehensive language specifications and error documentation.

## Troubleshooting C++ Compiler or Linker Errors

When the `stanc` compiler succeeds but C++ compilation fails, Make displays:

```
--- Compiling, linking C++ code ---
```

If compilation fails, report errors to the "Stan Forums" or "Stan compiler GitHub issues tracker."

## C++ Compilation and Linking Flags

Users can configure compiler and linker behavior through makefile variables. Configuration in the `make/local` file is recommended.

**Example:**
```
CXXFLAGS = -O2
```

### Optimization Settings

Setting `STAN_CPP_OPTIMS=true` in `make/local` enables tested optimizations. These "can speed up execution of certain models. We have observed speedups up to 15 percent, but this depends on the model, operating system and hardware used." However, these flags "considerably slow down compilation, so they are not used by default."

### Range Check Optimization

When indexing vectors, row_vectors, matrices, or arrays, Stan validates indices to prevent runtime errors. For performance-critical models, set `STAN_NO_RANGE_CHECKS=true` in `make/local` to remove these checks. This flag should be used only after "the indexing has been validated." Remove the flag for easier debugging if unexpected behavior occurs.

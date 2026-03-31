# Stan Reference Manual: Includes

## Overview

Stan supports file inclusion functionality comparable to C++ preprocessor directives. When you include a file, its contents replace the include statement in the source code.

## Basic Usage

A typical workflow involves defining reusable functions in a separate file. For instance, `my-std-normal.stan` might contain:

```stan
functions {
  real my_std_normal_lpdf(vector y) {
    return -0.5 * y' * y;
  }
}
```

Then in your main program:

```stan
#include my-std-normal.stan
parameters {
  real y;
}
model {
  y ~ my_std_normal();
}
```

The preprocessor effectively merges both files into a single program, placing the included content where the directive appears.

## Formatting Flexibility

**Whitespace handling:** The `#` symbol can have leading whitespace; initial spacing gets discarded during processing.

**Comments permitted:** Line-based comments may follow include statements. These comments are removed when the file's contents substitute the directive:

```stan
#include my-std-normal.stan  // definition of standard normal
```

## Recursive Includes

Circular dependencies cause compilation errors. For example, if `a.stan` includes `b.stan` and vice versa, the compiler reports the circular dependency and halts processing.

## Include Path Resolution

Stan interfaces can specify system paths for searching included files. The system locates the first matching filename in the sequence. Paths without trailing `/` or `\` automatically receive one between the path and filename.

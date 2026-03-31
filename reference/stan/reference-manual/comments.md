# Comments in Stan

## Overview

Stan supports two comment styles borrowed from C++: line-based and bracketed comments. These can be placed anywhere whitespace is allowed in a Stan program.

## Line-Based Comments

Line comments begin with two forward slashes (`//`) and extend to the end of the line. Everything following the slashes is ignored.

Example usage for documentation:

```stan
data {
  int<lower=0> N;  // number of observations
  array[N] real y;  // observations
}
```

## Bracketed Comments

Bracketed comments use `/* */` delimiters. Any text between `/*` and `*/` is ignored, allowing comments to span multiple lines or appear mid-line.

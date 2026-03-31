# Using the Stan Compiler

## Overview

Stan employs the **stanc3 compiler**, implemented in OCaml since version 2.22. The binary remains named `stanc`, with both terms used interchangeably in documentation.

## Command-Line Syntax

```
stanc (options) <model_file>
```

Where `<model_file>` is a `.stan` or `.stanfunctions` file path, or `'-'` for stdin.

## Key Options

**Basic Operations:**
- `--help` / `-?` — Display complete option list
- `--version` — Show compiler version
- `--info` — Print model type information and distributions
- `--name=<model_name>` — Specify C++ class name
- `-o=<filename>` — Direct output to file

**Code Quality & Analysis:**
- `--auto-format` — Pretty-print to console with standardized formatting
- `--warn-pedantic` — Enable warnings about potential semantic issues
- `--warn-uninitialized` — Flag uninitialized variables (experimental)
- `--print-canonical` — Combine auto-format with canonicalization

**Advanced Features:**
- `--canonicalize=<options>` — Update deprecated syntax (supports: deprecations, parentheses, braces, includes, strip-comments)
- `--allow-undefined` — Permit declared but undefined functions
- `--standalone-functions` — Generate only function code
- `--include_paths=<dir1,...>` — Specify include directories
- `--max-line-length=<number>` — Set formatting line width (default: 78)

**Optimization Levels:**
- `--O0` (default) — No optimizations
- `--O1` — Basic optimizations (recommended)
- `--Oexperimental` — All optimizations (may slow compilation; not thoroughly tested)

**Other:**
- `--print-cpp` — Output generated C++ to stdout
- `--use-opencl` — Enable OpenCL features
- `--color` — Control error styling (auto/always/never)

## Error & Warning Types

**Warnings (non-fatal):**
- Empty model detection
- Deprecated feature usage
- Multiple warnings per compilation allowed

**Errors (fatal; one per run):**
1. **File errors** — Missing or inaccessible files
2. **Syntactic errors** — Lexing, include, or parsing violations
3. **Semantic errors** — Type mismatches and constraint violations
4. **Removal errors** — Use of deleted features
5. **Internal errors** — Compiler bugs (should be reported)

## Pedantic Mode (`--warn-pedantic`)

Identifies potential statistical or programming issues:

- **Distribution argument mismatches** — Parameters inconsistent with distribution requirements
- **Uniform distribution usage** — Warns unless constraints exactly match bounds
- **Gamma/Inverse-Gamma patterns** — Detects improper prior attempts
- **LKJ correlation** — Recommends Cholesky variant
- **Unused parameters** — Variables not affecting `target`
- **Extreme constants** — Values <0.1 or >10 in distribution arguments
- **Parameter-dependent control flow** — Branching conditions depending on parameters
- **Multiple tildes** — Parameter appearing in multiple `~` statements
- **Zero or multiple priors** — Parameters with inconsistent prior specification
- **Uninitialized variables** — Use before assignment
- **Strict parameter bounds** — Hard constraints on parameters (except `<0,1>` and `<-1,1>`)
- **Nonlinear transformations** — Flagged when Jacobian adjustment may be needed

**Limitations:**
- Constant evaluation is finite and may be incomplete
- Indexed variables treated conservatively
- Data variable declarations ignored
- Nested function parameter-dependent control flow not detected

## Automatic Formatting & Canonicalization

**Formatting** (`--auto-format`):
- Regularizes spacing, indentation, and line length
- Default splits at column 78; customize with `--max-line-length`
- Preserves program structure while cleaning presentation

**Canonicalization** (via `--canonicalize`):
- `deprecations` — Replace outdated functions
- `parentheses` — Remove unnecessary grouping
- `braces` — Add braces around single-statement blocks
- `includes` — Inline included files (new default; omit to preserve directives)

**Known Issues:**
- Comments in unusual positions may relocate (prefixed with `^^^:`)
- Atypical `#include` placement may fail without inlining

## Optimization Details

**O1 Optimizations:**
- Dead code elimination
- Copy propagation
- Constant propagation
- Partial evaluation
- Function inlining
- Matrix memory layout optimization (AoS vs. SoA)

**Oexperimental Additional Optimizations:**
- Automatic-differentiation level optimization
- One-step loop unrolling
- Expression propagation
- Lazy code motion (common-subexpression elimination, loop-invariant motion)
- Static loop unrolling

**Debug Flags:**
- `--debug-optimized-mir-pretty` — Show optimized representation
- `--debug-transformed-mir-pretty` — Show pre-optimization representation
- `--debug-mem-patterns` — Report matrix memory layout choices

# Stan Language Syntax Documentation

## Overview

This page documents the complete syntax of the Stan modeling language using Backus-Naur form (BNF) grammar with additional constraints. The content is organized into BNF grammar definitions, tokenizing rules, and extra-grammatical constraints.

## BNF Grammars

### Syntactic Conventions

The grammar uses standard notation: tokens appear in ALLCAPS, non-terminals use angle brackets, square brackets indicate optional elements, and asterisks denote zero or more repetitions. "Parameterized nonterminals" allow generic rules like `<list(x)>` to be applied to different symbol types.

### Program Structure

A Stan program may contain up to seven blocks in sequence:
- `functions` (optional)
- `data` (optional)
- `transformed data` (optional)
- `parameters` (optional)
- `transformed parameters` (optional)
- `model` (optional)
- `generated quantities` (optional)

Programs can also contain only function definitions via the `<functions_only>` rule.

### Function Declarations

Functions require: return type, identifier, parameter list in parentheses, and a statement body. Return types can be void or an unsized type. Parameters may optionally be tagged with the `data` qualifier.

### Variable Declarations

Variable declarations specify type, identifier, optional dimensions, optional assignment, and end with semicolon. Stan supports sized and unsized types, with constrained types for parameters including ranges, ordering constraints, simplex constraints, and matrix structure constraints.

### Expressions

Expressions support:
- Ternary conditional operator (`?:`)
- Binary operators (arithmetic, logical, comparison)
- Prefix operators (`!`, `-`, `+`)
- Postfix operators (transpose)
- Function calls with optional conditioning bar syntax
- Array/matrix indexing with slice notation
- Array construction with braces

### Statements

Atomic statements include assignments, function calls, sampling statements with optional truncation, target increment operations, flow control (break/continue), and I/O (print/reject/fatal_error). Nested statements include conditionals, loops, profile blocks, and compound statements.

## Tokenizing Rules

Identifiers: begin with letter, followed by alphanumerics or underscores

String literals: enclosed in double quotes

Numeric literals support:
- Integer numerals with optional underscores: `[0-9]+ (_ [0-9]+)*`
- Real numerals with decimal points and optional exponents
- Imaginary numerals appended with `i`
- Dot numerals for field access: `\. [0-9]+`

## Extra-Grammatical Constraints

**Type Constraints**: Functions and distributions enforce specific type requirements; violations cause compilation errors.

**Operator Precedence**: Disambiguates expressions like "1 + 2 * 3" according to standard precedence rules.

**Array Element Typing**: Elements in array expressions must be the same type or scalar types (promoted along the int->real->complex hierarchy).

**Numeric Forms**: Multi-digit integers cannot start with zero; real literals cannot be only a period or exponent.

**Conditional Requirements**: If-then-else and while-loop conditions require integer or real primitive types.

**Loop Variables**: For loops require either a range of two integers or a container expression; loop variables cannot shadow existing variables.

**Function Naming Conventions**: Functions ending in `_rng` allowed only in transformed data and generated quantities blocks; `_lupmf`/`_lupdf` functions only in model block; `_lp` functions restricted appropriately; `jacobian +=` only in transformed parameters or `_jacobian` functions.

**Probability Functions**: Must end with `_lpdf`, `_lpmf`, `_lcdf`, or `_lccdf` suffix.

**Indexing Rules**: Indexes must be integers or integer arrays; total indexes cannot exceed variable dimensions (accounting for vector/matrix structure).

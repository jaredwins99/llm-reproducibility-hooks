# RDump Format for CmdStan

## Overview

RDump format represents values for Stan variables, though the documentation notes: "Although the RDump format is still supported, I/O with JSON is faster and recommended."

This format originated in SPLUS and is used across R, JAGS, and BUGS (with different ordering in BUGS).

## Creating Dump Files

Dump files must be created using RStan's `stan_rdump` function rather than R's native `dump` function, as the latter uses syntax unsupported by Stan's I/O libraries.

## Variable Types and Syntax

### Scalar Variables

Simple assignment using SPLUS syntax:
```
y <- 17.2
```

### Sequence Variables

One-dimensional arrays using sequence notation:
```
n <- c(1,2,3)
y <- c(2.0,3.0,9.7)
```

Colon-based notation for sequences:
```
n <- 1:3
n <- 2:-2
```

Special zero-sequence representations:
```
x1 <- integer()
x2 <- integer(0)
x3 <- integer(2)
y1 <- double()
y2 <- double(0)
y3 <- double(2)
```

### Array Variables

Multi-dimensional arrays use `structure` with dimensionality declaration:
```
y <- structure(c(1,2,3,4,5,6), .Dim = c(2,3))
y <- structure(1:6, .Dim = c(2,3))
```

Data storage follows **column-major** ordering:
- y[1,1]=1, y[1,2]=3, y[1,3]=5
- y[2,1]=2, y[2,2]=4, y[2,3]=6

Three-dimensional example:
```
z <- structure(1:24, .Dim = c(2,3,4))
```

Arrays with zero dimensions:
```
y <- structure(integer(), .Dim = c(2,0))
```

### Vector and Matrix Variables

Vectors, row vectors, and matrices use the same format as corresponding array shapes:
```
array[K] real a;
vector[K] b;
row_vector[K] c;
```

Matrix format:
```
array[M, N] real a;
matrix[M, N] b;
```

Arrays of vectors and matrices follow array indexing before container indexing:
```
array[M, N] real a;
matrix[M, N] b;
array[M] vector[N] c;
array[M] row_vector[N] d;
```

Three-dimensional equivalents:
```
array[P, M, N] real a;
array[P] matrix[M, N] b;
array[P, M] vector[N] c;
array[P, M] row_vector[N] d;
```

### Complex Numbers

"At this time, there is no support for complex number input through the R dump format. As an alternative, the JSON input format supports complex numbers."

### Integer and Real Values

Type inference is automatic:
- **No decimal point or scientific notation** -> can assign to `int` or `real`
- **Decimal point present** (e.g., 132.3) -> inferred as real
- **Scientific notation** (e.g., 1.323e2) -> inferred as real
- **Array with mixed formats** -> must be all integers for `int` array

Examples:
```
y <- 2          # integer or real
y <- 2L         # explicit long integer
y <- 2.0        # real-valued
y <- 1e+06      # scientific notation (real only)
```

### Special Numeric Values

Supported infinite and NaN representations:

| Value | Preferred | Alternatives |
|-------|-----------|--------------|
| Positive infinity | `Inf` | Infinity, infinity |
| Negative infinity | `-Inf` | -Infinity, -infinity |
| Not-a-number | `NaN` | (case insensitive) |

Case-insensitive: `inf`, `NAN` are valid.

### Quoted Variable Names

Variables may be double-quoted for JAGS compatibility:
```
"y" <- c(1,2,3)
```

### Line Breaks

Line breaks allowed after assignment operator:
```
y <- 2
y <-
3
```

Invalid: breaking before assignment operator
```
y
<- 2    # Syntax Error
```

Valid breaks within sequences and dimension declarations:
```
y <-
structure(c(1,2,3,
4,5,6,7,8,9,10,11,
12), .Dim = c(2,2,
3))
```

## BNF Grammar

```
definition ::= name <- value optional_semicolon

name ::= char*     | ''' char* '''     | '"' char* '"'

value ::= value<int> | value<double>

value<T> ::= T       | seq<T>       | zero_array<T>       |
'structure' '(' seq<T> ',' ".Dim" '=' seq<int> ')'       | 'structure'
'(' zero_array<T> ',' ".Dim" '=' seq<int> ')'

seq<int> ::= int ':' int       | cseq<int>

zero_array<int> ::= "integer" '(' <non-negative int>? ')'

zero_array<real> ::= "double" '(' <non-negative int>? ')'

seq<real> ::= cseq<real>

cseq<T> ::= 'c' '(' vseq<T> ')'

vseq<T> ::= T      | T ',' vseq<T>
```

Integer sequences may be assigned to either integer or real variables in Stan due to automatic promotion.

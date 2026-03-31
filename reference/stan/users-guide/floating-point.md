# Floating Point Arithmetic

## Overview

Computers represent real values using a fixed number of bits. Stan implements double-precision arithmetic following the IEEE 754 standard.

## Floating-Point Representations

### Finite Values

Double-precision uses 64 bits divided into:
- **Significand** (53 bits): base value representing significant digits
- **Exponent** (11 bits): power of two multiplied by the base

The value formula: v = (-1)^s * c * 2^q

### Normality

Normal floating-point values have no leading zeros in the significand. Subnormal numbers may use leading zeros, though not all I/O systems support them.

### Ranges and Extreme Values

Legal exponent values range from -(2^10) + 2 = -1022 to 2^10 - 1 = 1023. Legal significand values span -2^52 to 2^52 - 1.

Extreme values include:
- Largest normal finite: approximately 1.8 x 10^308
- Largest subnormal finite: approximately 2.2 x 10^308
- Smallest positive normal: approximately 2.2 x 10^-308
- Smallest positive subnormal: approximately 4.9 x 10^-324

### Signed Zero

Two representations of zero exist: "positive zero" and "negative zero." Both are equal in Stan (as in R): `0 == -0` returns true.

### Not-a-Number Values

Stan provides `not_a_number()` to return NaN values and `is_nan(x)` to test for them. NaN propagates through most mathematical operations. Comparisons with NaN return false, including `not_a_number() == not_a_number()`. However, `not_a_number() != not_a_number()` returns true. Undefined operations like `sqrt(-1)` return NaN.

### Positive and Negative Infinity

Stan provides `positive_infinity()`, `negative_infinity()`, and `is_inf()` functions. Positive infinity plus finite values yields positive infinity. Subtracting positive infinity from itself produces NaN, as does dividing infinite values.

## Literals: Decimal and Scientific Notation

Numbers use standard decimal notation (e.g., `2.39`, `-1567846.276452`). Scientific notation combines signed decimal base with signed integer exponent (e.g., `36.29e-3` = 0.03629). Maximum practical precision is 16 significant digits.

## Arithmetic Precision

The 53-bit significand provides approximately 15.95 decimal digits of precision. However, chained operations typically yield lower realized precision.

### Rounding and Probabilities

Finite precision causes rounding; numbers represent the closest floating-point value. Example: `1 + 1e-20 == 1` (rounds to 1), but `0 + 1e-20 == 1e-20`. Precision depends on scale.

Rounding breaks transitivity: (a + b) + c typically does not equal a + (b + c) for floating-point numbers.

Statistical implications: Cholesky factors L satisfying L*L^T may become non-symmetric or non-positive-definite due to rounding. Remedies include averaging L*L^T with its transpose or adding small diagonal quantities.

### Machine Precision and Asymmetry of 0 and 1

Smallest positive number: approximately 0 + 10^-323
Largest number less than one: approximately 1 - 10^-15.93

Machine precision is approximately 10^-15.93, available via `machine_precision()` in Stan.

### Complementary and Epsilon Functions

Special functions mitigate rounding near one. For small x, `log(1 + x)` rounds the argument to 1 and result to zero. Stan provides `log1p(x)` implementing log(1 + x) with granularity for values near one.

Complementary cumulative distribution functions (CCDF) use F^c_Y(y) = 1 - F_Y(y) to represent values very close to one.

### Catastrophic Cancellation

Subtracting close numbers loses precision proportionally to closeness. Example:
```
1.23456789012345
-1.23456789012344
= 0.00000000000001
```

Fifteen decimal places of input precision yields one decimal place in output. Stan uses Welford's algorithm for variance computation to avoid catastrophic cancellation in single-pass calculations.

### Overflow

Results exceeding maximum representable values (e.g., `1e200 * 1e200`) overflow to positive infinity per IEEE 754. Overflow rarely affects statistical computations; log-scale alternatives exist when needed.

### Underflow and the Log Scale

Results too small to represent (e.g., `1e-200 * 1e-200`) underflow to zero. This ubiquitously affects likelihood calculations. With p(y_n | theta) < 0.1, the product underflows for N > 350.

Solution: work on log scale. Rather than computing:

$$\prod_{n=1}^{N} p(y_n \mid \theta)$$

Compute:

$$\sum_{n=1}^{N} \log p(y_n \mid \theta)$$

All Stan probability functions operate on the log scale.

## Log Sum of Exponentials

On log scale, multiplication becomes addition: log(a*b) = log a + log b. For addition, given log a and log b:

log(a + b) = log(exp(log a) + exp(log b))

### Log-Sum-Exp Function

The nested log of sum of exponentials is called "log-sum-exp":

log-sum-exp(u, v) = log(exp(u) + exp(v))

To prevent overflow, algebraic rearrangement yields:

log-sum-exp(u, v) = max(u, v) + log(exp(u - max(u, v)) + exp(v - max(u, v)))

Since terms inside exponentials are zero or negative, assuming u >= v:

log-sum-exp(u, v) = u + log(1 + exp(v - u))

The inner term can use `log1p`, though gains are limited because exp(v - u) approaches zero only when u >> v, likely rounding the final result to u anyway.

For log a > log b:

log(a + b) = log a + log1p(exp(log b - log a))

### Applying Log-Sum-Exp to a Sequence

Generalized to sequences v = v1, ..., vN:

$$\text{log-sum-exp}(v) = \log \sum_{n=1}^{N} \exp(v_n) = \max(v) + \log \sum_{n=1}^{N} \exp(v_n - \max(v))$$

Exponents cannot overflow (arguments are zero or negative). This enables computing log(u1 + ... + uN) given only log u_n.

### Calculating Means with Log-Sum-Exp

Computing mean of vector u entirely on log scale (given log u, returning log mean(u)):

$$\log\left(\frac{1}{N} \sum_{n=1}^{N} u_n\right) = -\log N + \text{log-sum-exp}(\log u)$$

where log u = (log u1, ..., log uN) is understood elementwise.

## Comparing Floating-Point Numbers

Exact equality testing is unreliable due to inexactness. Approximate comparison using tolerances is recommended.

**Absolute tolerance** (epsilon > 0):
```
abs(x - y) <= epsilon
```

Use when scale and relevant comparison are known.

**Relative tolerance** (epsilon > 0):
```
2 * abs(x - y) / (abs(x) + abs(y)) <= epsilon
```

---

**Note:** Intel optimizing compilers under certain optimization settings are notable exceptions to IEEE 754 compliance.

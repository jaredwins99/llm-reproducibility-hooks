# Real-Valued Basic Functions - Stan Functions Reference

## Overview

This documentation covers built-in functions that accept zero or more real or integer arguments and return real values. The chapter includes vectorization details, mathematical constants, special values, logical functions, arithmetic operators, and specialized mathematical functions.

## Vectorization of Real-Valued Functions

### Unary Function Vectorization

Many Stan functions apply elementwise to arrays, vectors, and matrices. When `exp()` is applied to an array, it processes each element individually. Integer arguments are promoted to real values while maintaining dimensionality.

**Real and Array Arguments Example:**
```stan
real y0 = exp(x0);
array[5] real y1 = exp(x1);
array[4, 7] real y2 = exp(x2);
```

**Vector and Matrix Arguments:**
```stan
vector[5] yv = exp(xv);
row_vector[7] yrv = exp(xrv);
matrix[10, 20] ym = exp(xm);
```

Integer arguments promote to real: if `n` is `int`, then `exp(n)` returns `real`.

### Binary Function Vectorization

Binary functions like `pow()` apply elementwise to arrays and combinations of scalars with containers. When both arguments are arrays, they must have identical dimensions. Scalar values broadcast to match array dimensions.

**Array-to-Array Application:**
```stan
real y0 = pow(x00, x01);
array[5] real y1 = pow(x10, x11);
array[4, 7] real y2 = pow(x20, x21);
```

**Scalar Broadcast:**
```stan
y2 = pow(x20, x00);  // x00 broadcasts to each element
```

**Vector and Matrix Application:**
```stan
vector[5] yv = pow(xv00, xv01);
row_vector[7] yrv = pow(xrv, x00);
matrix[10, 20] ym = pow(x00, xm);
```

**Type Requirements:** Both inputs must be the same container type and size, except one can be real. Integer-requiring functions (e.g., `bessel_first_kind`) allow one integer array argument with matching dimensions.

---

## Mathematical Constants

Constants are invoked as zero-argument functions.

| Function | Returns |
|----------|---------|
| `pi()` | pi, the ratio of a circle's circumference to diameter |
| `e()` | e, the base of natural logarithm |
| `sqrt2()` | sqrt(2), the square root of 2 |
| `log2()` | Natural logarithm of 2 |
| `log10()` | Natural logarithm of 10 |

*Available since 2.0*

---

## Special Values

| Function | Returns |
|----------|---------|
| `not_a_number()` | NaN, a non-finite real value signaling an error |
| `positive_infinity()` | Positive infinity, larger than all finite numbers |
| `negative_infinity()` | Negative infinity, smaller than all finite numbers |
| `machine_precision()` | The smallest x where (x + 1) != 1 in floating-point arithmetic |

*Available since 2.0*

---

## Log Probability Function

`real target()`

Returns the current value of the log probability accumulator. Used primarily for debugging to observe the accumulator at various execution stages. This function may only be used in the model block.

*Available since 2.10*

---

## Logical Functions

### Comparison Operators

All return boolean (0 or 1). Integer and real versions exist; mixed types promote integers to real.

| Operator | Behavior |
|----------|----------|
| `operator<(x, y)` | 1 if x < y, else 0 |
| `operator<=(x, y)` | 1 if x <= y, else 0 |
| `operator>(x, y)` | 1 if x > y, else 0 |
| `operator>=(x, y)` | 1 if x >= y, else 0 |
| `operator==(x, y)` | 1 if x = y, else 0 |
| `operator!=(x, y)` | 1 if x != y, else 0 |

*Available since 2.0*

### Boolean Operators

Non-zero values are treated as true; zero as false. Precedence: negation (tightest) > conjunction > disjunction.

| Operator | Behavior |
|----------|----------|
| `operator!(x)` | 1 if x equals 0, else 0 |
| `operator&&(x, y)` | 1 if both x and y are non-zero |
| `operator\|\|(x, y)` | 1 if x or y is non-zero |

**Short-Circuiting:** In `a && b`, if `a` is false, `b` is not evaluated. In `a || b`, if `a` is true, `b` is not evaluated.

*Available since 2.0; `operator!` and real versions of `&&` and `||` deprecated in 2.31*

### Logical Functions

`real step(real x)`

Returns 1 if x is positive, 0 otherwise. **Warning:** `step(0)` and `step(NaN)` return 1, whereas `int_step(0)` and `int_step(NaN)` return 0. This is a step-like function; see section on step functions for warnings about use with parameters.

*Available since 2.0*

`int is_inf(real x)`

Returns 1 if x is infinite (positive or negative), 0 otherwise.

*Available since 2.5*

`int is_nan(real x)`

Returns 1 if x is NaN, 0 otherwise.

*Available since 2.5*

**Caution:** Both `is_inf()` and `is_nan()` are step-like and can cause gradient discontinuities when applied to parameters.

---

## Real-Valued Arithmetic Operators

### Binary Infix Operators

| Operator | Function |
|----------|----------|
| `x + y` | Sum of x and y |
| `x - y` | Difference of x and y |
| `x * y` | Product of x and y |
| `x / y` | Quotient of x divided by y |
| `x ^ y` | x raised to power y |

*Available since 2.0; `^` available since 2.5*

### Unary Prefix Operators

| Operator | Function |
|----------|----------|
| `-x` | Negation of x |
| `+x` | Value of x (no change) |

The negation operator is vectorized: `-x` negates each element of arrays, vectors, or matrices.

*Available since 2.0; vectorized negation since 2.31*

---

## Step-Like Functions

**Warning:** These functions seriously hinder sampling and optimization efficiency for gradient-based methods (NUTS, HMC, BFGS) when applied to parameters due to gradient discontinuities. They do not hinder sampling when used in data, transformed data, or generated quantities blocks.

### Absolute Value Functions

`T abs(T x)`

The absolute value of x. Works elementwise over vectors, row_vectors, matrices, and arrays thereof.

*Available since 2.0, vectorized in 2.30*

`real fdim(real x, real y)`

Returns the positive difference: x - y if x >= y, else 0.

*Available since 2.0*

`R fdim(T1 x, T2 y)`

Vectorized version of `fdim`.

*Available since 2.25*

### Bounds Functions

`real fmin(real x, real y)`

Returns the minimum of x and y.

*Available since 2.0*

`R fmin(T1 x, T2 y)`

Vectorized version of `fmin`.

*Available since 2.25*

`real fmax(real x, real y)`

Returns the maximum of x and y.

*Available since 2.0*

`R fmax(T1 x, T2 y)`

Vectorized version of `fmax`.

*Available since 2.25*

### Arithmetic Functions

`real fmod(real x, real y)`

Returns the remainder after dividing x by y: x - floor(x/y) * y.

*Available since 2.0*

`R fmod(T1 x, T2 y)`

Vectorized version of `fmod`.

*Available since 2.25*

### Rounding Functions

**Warning:** Rounding functions convert reals to integers. Gradient information from functions applied to the integer result is not passed to the original real value. The `to_int()` function can be used for data or generated quantities blocks.

| Function | Definition |
|----------|-----------|
| `R floor(T x)` | Largest integer <= x, converted to real |
| `R ceil(T x)` | Smallest integer >= x, converted to real |
| `R round(T x)` | Nearest integer to x, converted to real |
| `R trunc(T x)` | Integer nearest to x with no larger magnitude, as double |

*Available since 2.0, vectorized in 2.13*

---

## Power and Logarithm Functions

| Function | Returns |
|----------|---------|
| `R sqrt(T x)` | Square root of x |
| `R cbrt(T x)` | Cube root of x |
| `R square(T x)` | Square of x |
| `R exp(T x)` | Natural exponential of x |
| `R exp2(T x)` | Base-2 exponential of x |
| `R log(T x)` | Natural logarithm of x |
| `R log2(T x)` | Base-2 logarithm of x |
| `R log10(T x)` | Base-10 logarithm of x |
| `real pow(real x, real y)` | x raised to power y |
| `R pow(T1 x, T2 y)` | Vectorized power function |
| `R inv(T x)` | Inverse (reciprocal) of x |
| `R inv_sqrt(T x)` | Inverse of square root of x |
| `R inv_square(T x)` | Inverse of square of x |

*Available since 2.0, vectorized in 2.13 (except pow, which is 2.25)*

---

## Trigonometric Functions

`real hypot(real x, real y)`

Returns the hypotenuse length: sqrt(x^2 + y^2) if x, y >= 0, else NaN.

*Available since 2.0*

`R hypot(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

| Function | Returns |
|----------|---------|
| `R cos(T x)` | Cosine of x (radians) |
| `R sin(T x)` | Sine of x (radians) |
| `R tan(T x)` | Tangent of x (radians) |
| `R acos(T x)` | Arc cosine of x (radians) |
| `R asin(T x)` | Arc sine of x (radians) |
| `R atan(T x)` | Arc tangent of x, range (-pi/2, pi/2) |
| `R atan2(T y, T x)` | Arc tangent of y/x with quadrant correction |

*Available since 2.0, vectorized in 2.13 (atan2 in 2.34)*

---

## Hyperbolic Trigonometric Functions

| Function | Returns |
|----------|---------|
| `R cosh(T x)` | Hyperbolic cosine of x |
| `R sinh(T x)` | Hyperbolic sine of x |
| `R tanh(T x)` | Hyperbolic tangent of x |
| `R acosh(T x)` | Inverse hyperbolic cosine |
| `R asinh(T x)` | Inverse hyperbolic sine |
| `R atanh(T x)` | Inverse hyperbolic tangent |

*Available since 2.0, vectorized in 2.13*

---

## Link Functions

| Function | Returns |
|----------|---------|
| `R logit(T x)` | Log odds function |
| `R inv_logit(T x)` | Logistic sigmoid function |
| `R inv_cloglog(T x)` | Inverse complementary log-log function |

*Available since 2.0, vectorized in 2.13. Phi (normal CDF) also serves as a link function.*

---

## Probability-Related Functions

### Normal Cumulative Distribution Functions

`R erf(T x)`

Error function (Gauss error function).

*Available since 2.0, vectorized in 2.13*

`R erfc(T x)`

Complementary error function.

*Available since 2.0, vectorized in 2.13*

`R inv_erfc(T x)`

Inverse complementary error function.

*Available since 2.29, vectorized in 2.29*

`R Phi(T x)`

Standard normal cumulative distribution function.

*Available since 2.0, vectorized in 2.13*

`R inv_Phi(T x)`

Inverse standard normal CDF (quantile function). Algorithm from Wichura (1988). Untested for quantiles below 1e-16; errors increase for quantiles above 0.999999999.

*Available since 2.0, vectorized in 2.13*

`R Phi_approx(T x)`

Fast approximation of Phi with maximum absolute error of 0.00014 (Bowling et al. 2009).

*Available since 2.0, vectorized in 2.13*

### Other Probability-Related Functions

`real binary_log_loss(int y, real y_hat)`

Log loss for predicting y_hat in [0,1] for outcome y in {0,1}:
- Returns -log(y_hat) if y = 1
- Returns -log(1 - y_hat) otherwise

*Available since 2.0*

`R binary_log_loss(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real owens_t(real h, real a)`

Owen's T function for the probability P(X > h and 0 < Y < aX) where X, Y are independent standard normals.

*Available since 2.25*

`R owens_t(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

---

## Combinatorial Functions

`real beta(real alpha, real beta)`

Beta function for alpha, beta > 0. Computes the normalizing constant for the beta distribution.

*Available since 2.25*

`R beta(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real inc_beta(real alpha, real beta, real x)`

Regularized incomplete beta function up to x (see appendix for definition).

*Available since 2.10*

`real inv_inc_beta(real alpha, real beta, real p)`

Inverse of regularized incomplete beta: solves p = inc_beta(alpha, beta, x) for x.

*Available since 2.30*

`real lbeta(real alpha, real beta)`

Natural logarithm of beta function:
```
log(Gamma(alpha)) + log(Gamma(beta)) - log(Gamma(alpha + beta))
```

*Available since 2.0*

`R lbeta(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`R tgamma(T x)`

Gamma function. Generalizes factorial: Gamma(n+1) = n!. Defined for positive numbers and non-integral negatives.

*Available since 2.0, vectorized in 2.13*

`R lgamma(T x)`

Natural logarithm of gamma function.

*Available since 2.0, vectorized in 2.15*

`R digamma(T x)`

Digamma function (derivative of log-gamma). Defined for positive numbers and non-integral negatives.

*Available since 2.0, vectorized in 2.13*

`R trigamma(T x)`

Trigamma function (second derivative of log-gamma).

*Available since 2.0, vectorized in 2.13*

`real lmgamma(int n, real x)`

Natural logarithm of multivariate gamma function Gamma_n with n dimensions applied to x (see appendix for definition).

*Available since 2.0*

`R lmgamma(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real gamma_p(real a, real z)`

Normalized lower incomplete gamma function for a > 0, z >= 0:
```
(1/Gamma(a)) integral_0^z t^(a-1) e^(-t) dt
```

*Available since 2.0*

`R gamma_p(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real gamma_q(real a, real z)`

Normalized upper incomplete gamma function for a > 0, z >= 0:
```
(1/Gamma(a)) integral_z^inf t^(a-1) e^(-t) dt
```

*Available since 2.0*

`R gamma_q(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`int choose(int x, int y)`

Binomial coefficient ("x choose y"). For 0 <= y <= x:
```
x! / (y! * (x - y)!)
```

*Available since 2.14*

`R choose(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real bessel_first_kind(int v, real x)`

Bessel function of the first kind with order v:
```
J_v(x) = (x/2)^v sum_{k=0}^inf ((-x^2/4)^k) / (k! Gamma(v+k+1))
```

*Available since 2.5*

`R bessel_first_kind(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real bessel_second_kind(int v, real x)`

Bessel function of the second kind with order v for x, v > 0:
```
Y_v(x) = (J_v(x) cos(v*pi) - J_{-v}(x)) / sin(v*pi)
```

*Available since 2.5*

`R bessel_second_kind(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real modified_bessel_first_kind(int v, real z)`

Modified Bessel function of the first kind:
```
I_v(z) = (z/2)^v sum_{k=0}^inf (z^2/4)^k / (k! Gamma(v+k+1))
```

*Available since 2.1*

`R modified_bessel_first_kind(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real log_modified_bessel_first_kind(real v, real z)`

Log of modified Bessel function of the first kind. v need not be integer.

*Available since 2.26*

`R log_modified_bessel_first_kind(T1 x, T2 y)`

Vectorized version.

*Available since 2.26*

`real modified_bessel_second_kind(int v, real z)`

Modified Bessel function of the second kind for z > 0, integer v:
```
K_v(z) = (pi/2) (I_{-v}(z) - I_v(z)) / sin(v*pi)
```

*Available since 2.1*

`R modified_bessel_second_kind(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real falling_factorial(real x, real n)`

Falling factorial for x > 0, real n:
```
(x)_n = Gamma(x+1) / Gamma(x-n+1)
```

*Available since 2.0*

`R falling_factorial(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real lchoose(real x, real y)`

Natural logarithm of generalized binomial coefficient. For 0 <= y <= x:
```
log(Gamma(x+1)) - log(Gamma(y+1)) - log(Gamma(x-y+1))
```

*Available since 2.10*

`R lchoose(T1 x, T2 y)`

Vectorized version.

*Available since 2.29*

`real log_falling_factorial(real x, real n)`

Log of falling factorial for x > 0, real n.

*Available since 2.0*

`real rising_factorial(real x, int n)`

Rising factorial for x > 0, integer n:
```
x^(n) = Gamma(x+n) / Gamma(x)
```

*Available since 2.20*

`R rising_factorial(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real log_rising_factorial(real x, real n)`

Log of rising factorial for x > 0, real n.

*Available since 2.0*

`R log_rising_factorial(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

---

## Composed Functions

These functions combine other operations with improved efficiency and numerical stability.

`R expm1(T x)`

Natural exponential of x minus 1.

*Available since 2.0, vectorized in 2.13*

`real fma(real x, real y, real z)`

Fused multiply-add: z + (x * y).

*Available since 2.0*

`real ldexp(real x, int y)`

Product of x and 2^y.

*Available since 2.25*

`R ldexp(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real lmultiply(real x, real y)`

Product of x and log(y):
- Returns 0 if x = y = 0
- Returns x * log(y) if x, y != 0
- Returns NaN otherwise

*Available since 2.10*

`R lmultiply(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`R log1p(T x)`

Natural logarithm of 1 plus x.

*Available since 2.0, vectorized in 2.13*

`R log1m(T x)`

Natural logarithm of 1 minus x.

*Available since 2.0, vectorized in 2.13*

`R log1p_exp(T x)`

Natural logarithm of 1 plus exp(x).

*Available since 2.0, vectorized in 2.13*

`R log1m_exp(T x)`

Logarithm of 1 minus exp(x).

*Available since 2.0, vectorized in 2.13*

`real log_diff_exp(real x, real y)`

Natural logarithm of the difference of exponentials:
- Returns log(exp(x) - exp(y)) if +inf > x >= y
- Returns -inf if x = y (includes case where both are -inf)
- Returns NaN otherwise

*Available since 2.0*

`R log_diff_exp(T1 x, T2 y)`

Vectorized version.

*Available since 2.25*

`real log_mix(real theta, real lp1, real lp2)`

Log mixture of log densities lp1 and lp2 with mixing proportion theta:
```
log(theta * exp(lp1) + (1 - theta) * exp(lp2))
= log_sum_exp(log(theta) + lp1, log(1 - theta) + lp2)
```

*Available since 2.6*

`R log_mix(T1 thetas, T2 lps)`

Generalized to multiple densities. thetas are mixing proportions (sum to 1), lps are log densities (1-d container matching thetas length or array thereof). Computes:
```
log(sum_n theta_n * exp(lp_n)) = log_sum_exp(log(theta) + lp)
```

*Available since 2.26*

`R log_sum_exp(T1 x, T2 y)`

Natural logarithm of sum of exponentials:
```
log(exp(x) + exp(y))
```

*Available since 2.0, vectorized in 2.33*

`R log_inv_logit(T x)`

Natural logarithm of inverse logit function.

*Available since 2.0, vectorized in 2.13*

`R log_inv_logit_diff(T1 x, T2 y)`

Natural logarithm of difference of inverse logits:
```
log(inv_logit(x) - inv_logit(y))
```

*Available since 2.25*

`R log1m_inv_logit(T x)`

Natural logarithm of 1 minus inverse logit function.

*Available since 2.0, vectorized in 2.13*

---

## Special Functions

`R lambert_w0(T x)`

Lambert W function, branch W_0. Solves W_0(x) * exp(W_0(x)) = x.

*Available since 2.25*

`R lambert_wm1(T x)`

Lambert W function, branch W_{-1}. Solves W_{-1}(x) * exp(W_{-1}(x)) = x.

*Available since 2.25*

---

## Hypergeometric Functions

Hypergeometric functions follow the power series form:
```
_pF_q(a_1,...,a_p; b_1,...,b_q; z) = sum_{n=0}^inf
  [(a_1)_n ... (a_p)_n / ((b_1)_n ... (b_q)_n)] * (z^n / n!)
```

where (a)_n is the Pochhammer symbol: (a)_n = Gamma(a+n) / Gamma(a).

Gradients with respect to parameters a_1, b_1, and z are computed using digamma functions and chain rules.

`real hypergeometric_1F0(real a, real z)`

Special case: p=1, q=0.

*Available since 2.37*

`real hypergeometric_2F1(real a1, real a2, real b1, real z)`

Special case: p=2, q=1. Applies Euler's transformation when convergence is poor:
```
2F1(a_1, a_2; b_1; z) = 2F1(b_1 - a_1, a_2; b_1; z/(z-1)) * (1-z)^(-a_2)
```

*Available since 2.37*

`real hypergeometric_3F2(T1 a, T2 b, real z)`

Special case: p=3, q=2. a is a length-3 vector, b is length-2 vector.

*Available since 2.37*

`real hypergeometric_pFq(T1 a, T2 b, real z)`

Generalized hypergeometric function. a is length-p vector, b is length-q vector.

*Available since 2.37*

---

## References

Bowling, Shannon R., Mohammad T. Khasawneh, Sittichai Kaewkuekool, and Byung Rae Cho. 2009. "A Logistic Approximation to the Cumulative Normal Distribution." *Journal of Industrial Engineering and Management* 2 (1): 114-27.

Wichura, Michael J. 1988. "Algorithm AS 241: The Percentage Points of the Normal Distribution." *Journal of the Royal Statistical Society. Series C (Applied Statistics)* 37 (3): 477-84.

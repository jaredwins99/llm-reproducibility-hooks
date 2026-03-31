# Stan Reference Manual: Statements

## Overview

Stan programs execute variable declarations and statements in written order. Unlike BUGS, variables must be assigned values before use. The foundation of Stan is evaluating a log probability function for parameter sets.

## Statement Block Contexts

Data and parameters blocks contain only declarations -- no statements allowed. All other blocks permit both declarations and statements.

## Assignment Statements

Assignment evaluates a right-hand expression and assigns it to a left-hand variable:

```stan
n = 0;
```

Type compatibility is required; integers promote to reals automatically. Self-assignment works:

```stan
n = n + 1;
```

Indexed assignments are valid for arrays, matrices, and vectors:

```stan
Sigma[1, 1] = 1.0;
```

### Promotion

Stan allows assignment from lower to higher types (int -> real -> complex) but not vice versa. Promotion extends to containers.

### Lvalues

Legal left-hand sides include:
- A variable
- An indexed variable
- A comma-separated list of lvalues in parentheses

An indexed variable needs sufficient dimensions matching the number of indices.

### Compound Arithmetic and Assignment

Operators can be combined with assignment:

```stan
x += 7;  // equivalent to x = x + 7
```

Supported operations: `+=`, `-=`, `*=`, `/=`, `.*=`, `./=`

## Increment Log Density

The `target` keyword increments the log probability function:

```stan
target += -0.5 * y * y;
```

This differs from a variable assignment -- `target` cannot be read as a variable directly (though `target()` function accesses its value).

For vectorized arguments, the sum is added to total log density.

## Distribution Statements

Distribution statements use tilde notation:

```stan
y ~ normal(mu, sigma);
mu ~ normal(0, 10);
sigma ~ normal(0, 1);
```

These expand to equivalent `target +=` statements using `_lpdf` (continuous) or `_lpmf` (discrete) functions. Multiple identical statements compound multiplicatively.

Distribution statements drop constant terms for efficiency; explicit `_lpdf` calls retain all terms.

### User-Transformed Variables

Applying nonlinear transforms to parameters requires Jacobian adjustment:

```stan
log(beta) ~ normal(mu, sigma);  // needs adjustment
target += -log(abs(beta));       // log Jacobian
```

### Truncated Distributions

Distributions support truncation with bounds:

```stan
y ~ normal(0, 1) T[-0.5, 2.1];  // both bounds
y ~ normal(0, 1) T[0, ];        // lower only
y ~ normal(0, 1) T[, 2.1];      // upper only
```

Truncation requires corresponding log CDF/CCDF functions. Values outside bounds add negative infinity to target.

## For Loops

Standard for loops with integer bounds:

```stan
for (n in 1:N) {
  y[n] ~ normal(mu, sigma);
}
```

Loop variables are implicitly `int` with scope limited to the loop body. Ranges execute upward (e.g., `5:2` executes nothing).

Stan allows variable reassignment in loops, unlike BUGS. Execution order matters:

```stan
for (n in 1:N) {
  theta = inv_logit(alpha + x[n] * beta);
  y[n] ~ bernoulli(theta);
}
```

## Foreach Loops

Iteration over container elements:

```stan
for (y in ys) {
  // ... use y ...
}
```

- Vectors/row vectors: elements in order, `y` is double
- Matrices: column-major order, `y` is double
- Arrays: in order, `y` matches element type

Multi-dimensional arrays require nested loops.

## Conditional Statements

If-then-else syntax:

```stan
if (condition1)
  statement1
else if (condition2)
  statement2
else
  statementN
```

Conditions are integers (non-zero = true). Evaluation stops at first true condition.

## While Loops

```stan
while (condition)
  body
```

Conditions are integers. The loop executes repeatedly while true.

## Statement Blocks and Local Variables

Curly braces group statements; local variables declared at block start:

```stan
for (n in 1:N) {
  real theta;
  theta = inv_logit(alpha + x[n] * beta);
  y[n] ~ bernoulli(theta);
}
```

Local variable scope is the enclosing block. Stan prohibits variable hiding. Local variables cannot have constraints.

## Break and Continue Statements

- `break`: exits the innermost loop
- `continue`: skips to next loop iteration

Both must appear within loops but can be in nested statements:

```stan
while (1) {
  if (n < 0) break;
  foo(n);
  n = n - 1;
}
```

## Print Statements

Output literal strings and expression values:

```stan
print("loop iteration: ", n);
```

Format varies by type -- arrays/matrices use brackets, complex numbers use pairs. Print executes every statement invocation. Useful for debugging target values:

```stan
print("log density before =", target());
```

## Reject Statements

Signal errors or problematic values:

```stan
if (x < 0) {
  reject("x must not be negative; found x=", x);
}
```

Behavior depends on context:
- **Transformed data**: fatal
- **Transformed parameters/model**: equivalent to assigning negative infinity (rejects proposal)
- **Functions**: passed to caller

Reject should handle errors, not enforce arbitrary constraints. Use truncation (`T[a,b]`) for constraint-dependent bounds instead.

## Fatal Error Statements

Unconditionally halt execution:

```stan
fatal_error("unrecoverable error");
```

Useful in blocks where `reject` allows retry.

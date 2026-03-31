# Stan Reference Manual: Removed Features

This documentation page describes 12 functionalities that have been removed from the Stan programming language, along with their replacements.

## Key Removed Features

**`lp__` variable**: The direct access to the log probability variable was discontinued. Code using `lp__ <- lp__ + e;` should be replaced with `target += e;`. The value remains accessible through `target()`.

**Assignment operator `<-`**: This operator was removed in Stan 2.33. All assignments must now use `=` instead, changing `a <- b;` to `a = b;`.

**`increment_log_prob` statement**: Removed in Stan 2.33, this statement is replaced by `target += u;`.

**`get_lp()` function**: The no-argument function was discontinued in Stan 2.33 in favor of `target()`.

**Density and mass function suffixes**: The `_log` suffix (e.g., `foo_log(y, ...)`) was replaced with `_lpdf` for continuous distributions and `_lpmf` for discrete ones, using pipe notation: `foo_lpdf(y | ...)`.

**Distribution function alternatives**: `foo_cdf_log` became `foo_lcdf`, and `foo_ccdf_log` became `foo_lccdf`.

**`if_else` function**: Replaced by the conditional operator `a ? b : c;`, which provides better type flexibility.

**Comment syntax**: The `#` character for comments (outside `#include` statements) was removed in favor of `//`.

**Array declaration syntax**: Arrays changed from postfix notation (`int n[5]`) to prefix notation using the `array` keyword (`array[5] int n`).

**Real values in conditionals**: Using unqualified real numbers in `if` statements was prohibited in Stan 2.34, requiring explicit comparisons like `if (x != 0)`.

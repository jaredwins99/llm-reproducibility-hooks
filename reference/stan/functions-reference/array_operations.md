# Array Operations - Stan Functions Reference

## Reductions

### Minimum and Maximum

**`real min(array[] real x)`**
Returns the minimum value in x, or +inf if x is size 0.
*Available since 2.0*

**`int min(array[] int x)`**
Returns the minimum value in x, or error if x is size 0.
*Available since 2.0*

**`real max(array[] real x)`**
Returns the maximum value in x, or -inf if x is size 0.
*Available since 2.0*

**`int max(array[] int x)`**
Returns the maximum value in x, or error if x is size 0.
*Available since 2.0*

### Sum, Product, and Log Sum of Exp

**`int sum(array[] int x)`**
Returns the sum of elements in x, or 0 if empty.
*Available since 2.1*

**`real sum(array[] real x)`**
Returns the sum of elements in x.
*Available since 2.0*

**`complex sum(array[] complex x)`**
Returns the sum of elements in x.
*Available since 2.30*

**`real prod(array[] real x)`**
Returns the product of elements in x, or 1 if x is size 0.
*Available since 2.0*

**`real prod(array[] int x)`**
Returns the product of elements in x, defined as:
- prod(n=1 to N) x_n if N > 0
- 1 if N = 0

*Available since 2.0*

**`real log_sum_exp(array[] real x)`**
Returns the natural logarithm of the sum of exponentials of elements in x, or -inf if empty.
*Available since 2.0*

### Sample Mean, Variance, and Standard Deviation

**`real mean(array[] real x)`**
Computes sample mean: mean(x) = (1/N) sum(n=1 to N) x_n for N > 0.
Throws error if array size is 0.
*Available since 2.0*

**`real variance(array[] real x)`**
Computes sample variance:
- (1/(N-1)) sum(n=1 to N) (x_n - x_bar)^2 if N > 1
- 0 if N = 1

Throws error if array size is 0.
*Available since 2.0*

**`real sd(array[] real x)`**
Computes sample standard deviation:
- sqrt(variance(x)) if N > 1
- 0 if N = 0

Throws error if array size is 0.
*Available since 2.0*

### Norms

**`real norm1(vector x)`**
Computes the L1 norm: norm1(x) = sum(n=1 to N) |x_n|
*Available since 2.30*

**`real norm1(row_vector x)`**
Computes the L1 norm.
*Available since 2.30*

**`real norm1(array[] real x)`**
Computes the L1 norm.
*Available since 2.30*

**`real norm2(vector x)`**
Computes the L2 norm: norm2(x) = sqrt(sum(n=1 to N) x_n^2)
*Available since 2.30*

**`real norm2(row_vector x)`**
Computes the L2 norm.
*Available since 2.30*

**`real norm2(array[] real x)`**
Computes the L2 norm.
*Available since 2.30*

### Euclidean Distance and Squared Distance

**`real distance(vector x, vector y)`**
Computes Euclidean distance: distance(x,y) = sqrt(sum(n=1 to N) (x_n - y_n)^2)
Throws error if x and y have unequal sizes.
*Available since 2.2*

**`real distance(vector x, row_vector y)`**
Computes Euclidean distance.
*Available since 2.2*

**`real distance(row_vector x, vector y)`**
Computes Euclidean distance.
*Available since 2.2*

**`real distance(row_vector x, row_vector y)`**
Computes Euclidean distance.
*Available since 2.2*

**`real squared_distance(vector x, vector y)`**
Computes squared Euclidean distance: squared_distance(x,y) = sum(n=1 to N) (x_n - y_n)^2
Throws error if x and y have unequal sizes.
*Available since 2.7*

**`real squared_distance(vector x, row_vector y)`**
Computes squared Euclidean distance.
*Available since 2.26*

**`real squared_distance(row_vector x, vector y)`**
Computes squared Euclidean distance.
*Available since 2.26*

**`real squared_distance(row_vector x, row_vector y)`**
Computes squared Euclidean distance.
*Available since 2.26*

### Quantile

**`real quantile(data array[] real x, data real p)`**
Produces the p-th quantile of x using algorithm 7 from "Sample quantiles in Statistical Packages."
*Available since 2.27*

**`array[] real quantile(data array[] real x, data array[] real p)`**
Produces an array containing quantiles corresponding to an array of probabilities p.
*Available since 2.27*

## Array Size and Dimension Function

**`array[] int dims(T x)`**
Returns an integer array containing dimensions of x. Works for any Stan type with up to 8 array dimensions.
*Available since 2.0*

**`int num_elements(array[] T x)`**
Returns total number of elements in array x including all nested arrays, vectors, and matrices.
*Available since 2.5*

**`int size(array[] T x)`**
Returns number of top-level elements in array x.
*Available since 2.0*

## Array Broadcasting

**`array[] T rep_array(T x, int n)`**
Returns an n-element array with every entry assigned to x.
*Available since 2.0*

**`array [,] T rep_array(T x, int m, int n)`**
Returns an m by n array with every entry assigned to x.
*Available since 2.0*

**`array[,,] T rep_array(T x, int k, int m, int n)`**
Returns a k by m by n array with every entry assigned to x.
*Available since 2.0*

### Broadcasting Examples

Type distinction matters:
- `rep_array(1, 5)` produces `array[] int`
- `rep_array(1.0, 5)` produces `array[] real`

Integer arrays cannot be assigned to real arrays and vice versa.

When repeating a vector v of size 5: `rep_array(v, 27)` creates a size-27 array of 27 copies of v.

When T is itself an array, additional dimensions are added. For example:
```
array[5, 6] real a;
array[3, 4, 5, 6] real b;
b = rep_array(a, 3, 4);
```
After assignment, `b[j, k, m, n]` equals `a[m, n]` for j in 1:3, k in 1:4, m in 1:5, n in 1:6.

## Array Concatenation

**`T append_array(T x, T y)`**
Returns concatenation of two arrays x and y in argument order. T must be N-dimensional array (max N = 7) of any Stan type. All dimensions except first must match.
*Available since 2.18*

### Example
```
array[2, 1, 7] matrix[4, 6] x1;
array[3, 1, 7] matrix[4, 6] x2;
array[5, 1, 7] matrix[4, 6] x3;
x3 = append_array(x1, x2);
```

## Sorting Functions

**`array[] real sort_asc(array[] real v)`**
Sorts elements of v in ascending order.
*Available since 2.0*

**`array[] int sort_asc(array[] int v)`**
Sorts elements of v in ascending order.
*Available since 2.0*

**`array[] real sort_desc(array[] real v)`**
Sorts elements of v in descending order.
*Available since 2.0*

**`array[] int sort_desc(array[] int v)`**
Sorts elements of v in descending order.
*Available since 2.0*

**`array[] int sort_indices_asc(array[] real v)`**
Returns indices that would sort v in ascending order.
*Available since 2.3*

**`array[] int sort_indices_asc(array[] int v)`**
Returns indices that would sort v in ascending order.
*Available since 2.3*

**`array[] int sort_indices_desc(array[] real v)`**
Returns indices that would sort v in descending order.
*Available since 2.3*

**`array[] int sort_indices_desc(array[] int v)`**
Returns indices that would sort v in descending order.
*Available since 2.3*

**`int rank(array[] real v, int s)`**
Returns count of components in v less than v[s].
*Available since 2.0*

**`int rank(array[] int v, int s)`**
Returns count of components in v less than v[s].
*Available since 2.0*

### Sorting Example

For v = (1, -10.3, 20.987):
- sort_asc(v) = (-10.3, 1, 20.987)
- sort_desc(v) = (20.987, 1, -10.3)
- sort_indices_asc(v) = (2, 1, 3)
- sort_indices_desc(v) = (3, 1, 2)

## Reversing Functions

**`array[] T reverse(array[] T v)`**
Returns new array containing elements of v in reverse order.
*Available since 2.23*

### Reversing Example

For v = (1, -10.3, 20.987):
reverse(v) = (20.987, -10.3, 1)

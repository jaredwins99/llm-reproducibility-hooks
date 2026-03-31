# Stan Hypotheses vs. Reality

Ten questions about Stan's behavior, with predictions from first principles followed by verification against the reference documentation.

---

## 1. Can you declare a parameter that doesn't appear in the model block?

**Hypothesis**: Yes, Stan would allow it. The parameter would still get sampled but with an implicit improper uniform prior over its constrained space. HMC would see zero gradient with respect to this parameter, leading to a random walk.

**Reality**: The docs confirm all blocks are optional and parameters are declared without statements. The parameters block "declares sampling variables" and undergoes "inverse transformation to unconstrained space" with the "log Jacobian of transformation added to probability function." A parameter not mentioned in the model block would indeed receive only the Jacobian contribution -- effectively a flat (improper) prior on the constrained space. The sampler would still attempt to sample it, but with no likelihood or prior gradient, it would random-walk in unconstrained space.

**Verdict**: CORRECT

**Surprise**: None. The behavior follows directly from Stan's design.

---

## 2. Can you have a Stan model with NO model block at all?

**Hypothesis**: Yes, Stan would allow this. All parameters would get improper uniform priors. Could be useful for prior predictive simulation with generated quantities.

**Reality**: The docs explicitly state: "All blocks are optional; an empty program is valid (though generates a warning)." Since the model block is optional, a program with no model block is valid. With no model block, there are no log-probability increments, so parameters get flat priors (subject to constraint Jacobians).

**Verdict**: CORRECT

**Surprise**: Even a completely empty program is valid (with a warning). That is more permissive than expected.

---

## 3. Can you use a for loop inside a transformed parameters block?

**Hypothesis**: Yes. Stan is an imperative language, not purely declarative. The transformed parameters block allows "declarations and statements," so for loops should work fine.

**Reality**: The block summary table confirms transformed parameters allows "declarations and statements." The statements reference shows for loops are standard statements. The example program in the blocks doc even uses a for loop in the model block, and the same statement types are available in transformed parameters.

**Verdict**: CORRECT

**Surprise**: None. Stan's blocks differ in WHEN they execute and WHAT side effects are allowed, not in what control flow is permitted.

---

## 4. Can you pass a matrix as an argument to a user-defined function? What about returning one?

**Hypothesis**: Yes to both. Stan has matrix as a first-class type, so function signatures should accept and return matrices.

**Reality**: The user-functions reference confirms that valid base types for function arguments include "integer, real, complex, vector, row_vector, matrix, and tuple types." The `_rng` function example explicitly shows a function returning `matrix[N, K]`. Function arguments for vectors and matrices are "declared without size specifications" (sizes are inferred at call time). Constraints are not permitted in function declarations.

**Verdict**: CORRECT

**Surprise**: The detail that sizes are omitted in function argument declarations (just `matrix` not `matrix[M, N]`) is a nice design choice for genericity, though not surprising given Stan's type system.

---

## 5. Is there a way to do ragged arrays in Stan?

**Hypothesis**: Stan requires rectangular arrays. The workaround is to flatten ragged data into a single long array and use index arrays to slice it.

**Reality**: The sparse-ragged guide states explicitly: "Stan does not directly support either sparse or ragged data structures, though both can be accommodated with some programming effort." For ragged arrays, the solution is exactly as predicted: "combines a single vector holding all values sequentially" with "a separate integer array recording the size of each group." The `segment()` function is recommended for slicing, as it "allows for efficient vectorization."

**Verdict**: CORRECT

**Surprise**: None. The `segment()` function recommendation for slicing is a useful practical detail.

---

## 6. Can you put a print statement in the model block? Does it print once per iteration or once per leapfrog step?

**Hypothesis**: Yes, print is supported in the model block for debugging. It would print once per leapfrog step (since the model block is evaluated at each leapfrog step), making it very verbose.

**Reality**: The statements reference confirms: "Print executes every statement invocation." It even shows an example of printing `target()` in context. The blocks reference confirms the model block is evaluated per "leapfrog step." Therefore, print statements in the model block execute once per leapfrog step, not once per sample.

**Verdict**: CORRECT

**Surprise**: The docs explicitly show `print("log density before =", target());` as a debugging pattern, which is a nice practical tip.

---

## 7. Can you index a vector with another vector (like NumPy fancy indexing)?

**Hypothesis**: Yes, Stan supports multi-indexing with integer arrays, similar to fancy indexing.

**Reality**: Strongly confirmed. The expressions reference documents multiple indexing thoroughly. Using an integer array index: `a[ii]` produces `a[ii[1]], ..., a[ii[K]]`. The multi-indexing guide shows detailed examples like `c[idxs]` where `idxs` is an integer array. It also supports range indexing (`a[3:6]`), lower/upper bound indexing (`a[3:]`, `a[:5]`), and combinations thereof on matrices. Multiple indices can appear on both sides of assignments.

**Verdict**: CORRECT

**Surprise**: The indexing system is more comprehensive than I expected. It supports not just array-based fancy indexing but also range slicing (Python-style `a[3:6]`), open-ended ranges (`a[3:]`), and the "all" shorthand (`a[:]` or `a[]`). The aliasing safety (right-hand side evaluated fully before assignment) is also a thoughtful design choice.

---

## 8. What happens if you declare `real<lower=0> sigma;` but your prior allows negative values?

**Hypothesis**: Stan uses parameter transformations (log transform for lower-bounded parameters). The prior is evaluated on the constrained (positive) space. If the prior assigns density to negative values, those are simply unreachable -- Stan transforms, not hard-rejects. The wasted probability mass below 0 is harmless but inefficient.

**Reality**: The blocks reference confirms: the parameters block "undergoes inverse transformation to unconstrained space" and "Log Jacobian of transformation added to probability function." The execution reference details the process: (1) inverse transform unconstrained parameters to constrained form, (2) add log Jacobian, (3) execute model block. So Stan always works in unconstrained space and transforms back. A `normal(0,1)` prior on `sigma` with `lower=0` would evaluate the normal density only at positive values -- negative values literally cannot be reached because the transform (exp) maps all of R to R+. The types reference adds: "The model must have support (non-zero density, equivalently finite log density) at parameter values that satisfy the declared constraints."

**Verdict**: CORRECT

**Surprise**: The documentation's warning that "initializing parameters on the boundaries of their constraints is usually problematic" (because boundary values transform to infinite unconstrained values) is an important practical detail. The key principle that the model must have support at all constrained values is also worth noting -- if your prior had zero density everywhere on R+, that would be the real problem.

---

## 9. Can you do matrix multiplication with `*` or do you need a special function?

**Hypothesis**: `*` performs matrix multiplication (not elementwise). Elementwise multiplication uses `.*` (MATLAB convention).

**Reality**: Confirmed exactly. The expressions reference states that "multiplication extend to matrices, vectors, and row vectors" and shows that for vectors/matrices, `(y - mu)' * Sigma * (y - mu)` is valid and returns type `real`. Elementwise multiplication uses `.*` and elementwise division uses `./`. The matrices guide shows `y_hat = x * beta` as the efficient matrix-vector multiplication pattern.

**Verdict**: CORRECT

**Surprise**: Stan also has a left division operator `\` (backslash, precedence 3), which I did not predict. This is `A \ b` for solving `Ax = b`, similar to MATLAB.

---

## 10. Can a generated quantities block access the log probability (`target()`)?

**Hypothesis**: Probably NOT available in generated quantities. The `target` accumulator is used during sampling and may not be readable in the GQ block.

**Reality**: The statements reference says `target()` is a function that "accesses its value" and shows it used in a print statement context. The blocks reference says functions ending in `_lp` (which modify/access log probability) are "restricted to transformed parameters and model blocks." The generated quantities block is described as "independent of sampling process." However, the `target()` function for *reading* the value is distinct from `_lp` functions that *modify* it. The statements reference shows `target()` in a print context but does not explicitly restrict where `target()` can be called for reading.

Looking more carefully: the reference says `target` "cannot be read as a variable directly (though `target()` function accesses its value)." The `_lp` restriction applies to functions that *increment* target. The `target()` read function's availability in generated quantities is not explicitly confirmed or denied in these docs. However, the generated quantities block is described as executing "after sampling completes" and being "independent of sampling process," which suggests `target()` may not be meaningful there.

**Verdict**: PARTIALLY CORRECT (leaning toward correct intuition, but the docs are ambiguous)

**Surprise**: The distinction between `target +=` (writing, restricted to `_lp` contexts) and `target()` (reading) is subtle. The docs do not give a clear-cut answer about whether `target()` is callable in generated quantities. My intuition that it would not be available there seems reasonable given that GQ is "independent of sampling," but I cannot confirm this definitively from these references alone. In practice, Stan likely does not make `target()` available in GQ since the log probability accumulator is part of the sampling machinery.

---

## Summary

| # | Question | Verdict |
|---|----------|---------|
| 1 | Unused parameter in parameters block | CORRECT |
| 2 | Model with no model block | CORRECT |
| 3 | For loop in transformed parameters | CORRECT |
| 4 | Matrix as function argument/return | CORRECT |
| 5 | Ragged arrays | CORRECT |
| 6 | Print in model block | CORRECT |
| 7 | Vector indexing with another vector | CORRECT |
| 8 | Constraint vs. prior conflict | CORRECT |
| 9 | Matrix multiplication with * | CORRECT |
| 10 | target() in generated quantities | PARTIALLY CORRECT |

**Overall**: 9 correct, 1 partially correct, 0 wrong.

### Key Takeaways

1. Stan's design is highly principled -- most behaviors follow logically from understanding HMC and the block execution model.
2. The left division operator `\` was an unexpected find.
3. Stan's multi-indexing is richer than expected, with range slicing, open-ended ranges, and aliasing safety.
4. The `target()` read function vs. `target +=` write operation distinction is subtle and not fully documented in the references reviewed.
5. The "empty program is valid" permissiveness was mildly surprising.

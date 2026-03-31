# Transitioning from BUGS to Stan

## Overview

Stan and BUGS are superficially similar—both employ statistical modeling languages and can be invoked from R to run multiple chains—yet they differ substantially in implementation and capability.

## Key Operational Differences

**Compilation Model**: Unlike BUGS's interpreter, Stan compiles models in two stages: first to templated C++, then to platform-specific executables.

**Sampling Algorithm**: While BUGS updates one scalar parameter at a time using Gibbs sampling or adaptive rejection sampling, Stan employs Hamiltonian Monte Carlo (specifically the no-U-turn sampler) that explores the entire parameter space simultaneously.

**Warmup Phase**: BUGS tunes adaptive jumping during warmup, whereas Stan uses warmup to calibrate the NUTS sampler.

**Execution Model**: Stan's modeling language directly translates to executable C++ code with statements running sequentially, whereas BUGS parses its model to infer posterior density and determine sampling schemes.

**Gradient Computation**: Stan automatically computes log-density gradients using algorithmic differentiation, a requirement for HMC dynamics. BUGS computes densities only.

**Automation Level**: Both are semi-automatic, requiring users to specify chain count and iteration length. However, Stan's efficiency typically allows fewer iterations than BUGS for comparable results.

## Language Syntax Differences

Stan follows C conventions: line breaks are whitespace, statements end with semicolons. BUGS follows R conventions with meaningful line breaks.

Key distinctions include:

- **Variable naming**: Stan allows letters, numbers, underscores only (no periods); BUGS permits periods
- **Normal distribution parameterization**: Stan uses standard deviation (not variance or precision)
- **Multivariate distributions**: Stan specifies covariance matrices; BUGS uses precision matrices
- **Variable reassignment**: Stan allows overwriting intermediate quantities within blocks; BUGS prohibits this
- **Type declarations**: Stan requires explicit variable declarations with dimensions and bounds

Example Stan syntax:
```stan
for (i in 1:n)
  y[i] ~ normal(mu, sigma);
```

Or vectorized equivalently as:
```stan
y ~ normal(mu, sigma);
```

## Statistical Modeling Capabilities

**Discrete parameters**: Stan doesn't currently support declared discrete parameters, though inference is possible through mixture approaches.

**Implicit priors**: Undeclared parameters in Stan receive flat priors on their declared scale (bounded parameters get uniform priors; unbounded parameters get improper uniform priors).

**Multiple distribution statements**: Multiple sampling statements for the same variable multiply their densities rather than overwriting.

**Covariance matrices**: Stan includes distributions unavailable in BUGS, such as correlation matrix distributions and C-vine priors.

**Censoring/truncation**: Stan directly implements censored and truncated likelihoods.

## R Interface Differences

Running Stan from R requires setup but avoids recompilation on repeat executions when passing previous model results. Stan permits extra data variables that BUGS doesn't require, facilitating model exploration. RStan provides extraction functions for accessing simulations and sampler diagnostics unavailable in BUGS.

## Community and Licensing

Stan is licensed under the permissive BSD license (unlike BUGS's GPL or proprietary restrictions) and operates on Linux, Mac, and Windows platforms, matching BUGS availability.

# Stan Optimization Reference

## Overview

Stan offers optimization algorithms that identify modes of probability densities specified in Stan programs. These modes serve as parameter estimates or foundations for Bayesian posterior approximations.

The platform provides three optimization approaches: Newton's method, BFGS, and L-BFGS (the default). According to the documentation, "Newton's method is the least efficient of the three, but has the advantage of setting its own stepsize."

## Key Configuration Options

**Jacobian Adjustment**: All optimizers can include the log absolute Jacobian determinant of inverse parameter transforms. Without this adjustment (default), optimization finds modes in constrained parameter space. With adjustment, it finds modes in unconstrained space -- useful for Laplace approximation methods.

**Iteration Limits**: The default maximum iterations is 2000 for all optimizers.

**Progress Reporting**: Intermediate output streaming is configurable.

## Convergence Criteria (BFGS/L-BFGS)

The algorithms terminate when any tolerance threshold is satisfied. Convergence tests include:

**Parameter Convergence**: ||theta_i - theta_{i-1}|| < tol_param

**Density Convergence**: |log p(theta_i|y) - log p(theta_{i-1}|y)| < tol_obj (absolute) or relative tolerance tol_rel_obj

**Gradient Convergence**: ||g_i|| < tol_grad (absolute) or relative tolerance tol_rel_grad

## Practical Recommendations

For constrained parameters like standard deviations (sigma > 0), declaring unconstrained parameters can be "much more efficient" since the optimizer avoids extreme values. However, custom initialization within the parameter support is essential.

The documentation suggests testing both constrained and unconstrained formulations to determine which performs better for your specific problem.

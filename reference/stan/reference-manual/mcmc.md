# MCMC Sampling - Stan Reference Manual

## Overview

This reference manual chapter covers Markov chain Monte Carlo (MCMC) algorithms used in Stan, specifically Hamiltonian Monte Carlo (HMC) and the no-U-turn sampler (NUTS).

## Hamiltonian Monte Carlo

### Core Concepts

**Target Density**: The goal is sampling from a density p(theta) for parameters theta, typically a Bayesian posterior p(theta|y) given data y.

**Auxiliary Momentum Variables**: HMC introduces auxiliary momentum variables rho and draws from joint density:
- p(rho, theta) = p(rho | theta) p(theta)
- rho ~ MultiNormal(0, M), where M is the Euclidean metric

**The Hamiltonian**: Defined as:
- H(rho, theta) = T(rho | theta) + V(theta)
- T(rho | theta) = kinetic energy (momentum-based)
- V(theta) = potential energy (negative log posterior)

### Generating Transitions

1. Draw fresh momentum: rho ~ MultiNormal(0, M)
2. Evolve (theta, rho) using Hamilton's equations
3. Apply Metropolis acceptance step

Hamilton's equations (with momentum independent of target):
- d(theta)/dt = +dT/d(rho)
- d(rho)/dt = -dV/d(theta)

### Leapfrog Integrator

Stan uses the leapfrog algorithm for numerical integration. The algorithm:

1. Draws fresh momentum
2. Alternates half-step momentum updates with full-step position updates

Steps (repeated L times):
```
rho <- rho - (epsilon/2) dV/d(theta)
theta <- theta + epsilon M^{-1} rho
rho <- rho - (epsilon/2) dV/d(theta)
```

Where epsilon is step size and L is number of steps. Total integration time is L * epsilon.

**Error Analysis**: Leapfrog error is O(epsilon^3) per step, O(epsilon^2) globally.

### Metropolis Accept Step

Probability of accepting proposal (rho*, theta*) from (rho, theta):

min(1, exp(H(rho, theta) - H(rho*, theta*)))

If rejected, previous parameter value is retained.

### Algorithm Summary

For each iteration:
1. Sample new momentum vector
2. Update parameters using leapfrog integrator with step size epsilon and L steps
3. Apply Metropolis acceptance step
4. Decide whether to accept new state or keep existing state

## HMC Algorithm Parameters

Three parameters must be set:
- **Discretization time epsilon** (step size)
- **Metric M**
- **Number of steps L**

**Trade-offs**:
- If epsilon too large: inaccurate leapfrog integration, many rejections
- If epsilon too small: many steps required, long computation times
- If L too small: trajectory too short, random walk behavior
- If L too large: excessive computation per iteration
- Poor metric M^{-1}: requires smaller epsilon, larger L needed

### Integration Time

Actual integration time is L * epsilon. When interfaces specify approximate integration time t:

L = floor(t / epsilon)

### Automatic Parameter Tuning

Stan adapts parameters during warmup in three stages:

**Stage I (Initial Fast Interval)**: Chain converges toward typical set, fast parameters (like step size) adapted.

**Stage II (Slow Intervals)**: Growing, memoryless windows estimate parameters requiring global information (covariance).

**Stage III (Final Fast Interval)**: Fast parameters adapt to final slow parameter update.

**Default Adaptation Parameters**:
- Initial buffer: 75 iterations
- Term buffer: 50 iterations
- Window: 25 iterations (initial slow interval width)

### Discretization-Interval Adaptation Parameters

Stan uses dual averaging (Nesterov 2009) to optimize step size. Full parameters:

| Parameter | Description | Constraint | Default |
|-----------|-------------|-----------|---------|
| delta | Target Metropolis acceptance rate | [0, 1] | 0.8 |
| gamma | Adaptation regularization scale | (0, inf) | 0.05 |
| kappa | Adaptation relaxation exponent | (0, inf) | 0.75 |
| t_0 | Adaptation iteration offset | (0, inf) | 10 |

**Delta Effects**: Higher target acceptance rate (closer to 1) forces smaller step sizes, improving sampling efficiency at cost of increased iteration times. Can help models that would otherwise get stuck.

### Step-Size Jitter

Step size can be randomly jittered during sampling to avoid poor interactions with fixed step sizes and high-curvature regions. Jitter is a proportion (max 1.0), creating step size range [0, 2 * adapted_step_size]. Default is 0 (no jitter).

**Trade-off**: Jitter below adapted value increases leapfrog steps (slower); above adapted value causes premature rejection.

### Euclidean Metric

Three metric choices:
1. **Unit metric**: Diagonal matrix of ones
2. **Diagonal metric**: Diagonal matrix with positive entries (estimated during warmup)
3. **Dense metric**: Full symmetric positive definite matrix (regularized toward diagonal, then unit)

**Diagonal Metric**: Variances estimated from each slow-stage block using only that block's iterations, allowing early estimates to guide warmup without influencing final estimates. Uses Welford accumulators to prevent precision loss.

**Dense Metric**: Covariance estimated with regularization toward diagonal and unit metrics.

### Warmup Times and Estimating the Metric

The metric compensates for linear (global, position-independent) correlations. In complex models, global correlations are difficult to derive analytically. Stan estimates them online during adaptive warmup. In models with strong nonlinear correlations, learning is slow even with regularization, explaining long warmup requirements.

### Nonlinearity

Metrics only compensate for linear correlations. Nonlinear (local, position-dependent) correlations in hierarchical parameterizations require reparameterization or advanced algorithms like Riemannian HMC.

**Chicken-and-egg problem**: Appropriate metric requires convergence; convergence requires appropriate metric. Dense metrics are particularly difficult.

### Dense vs. Diagonal Metrics

Problematic sampling typically involves complex nonlinear correlations, not linear ones. Better approaches than dense metrics: improved parameterizations or advanced algorithms.

### Warmup Times and Curvature

MCMC convergence time approximates autocorrelation time. HMC chains have low autocorrelation, converging rapidly. However, non-uniform curvature across posterior violates this assumption. Often tails have large curvature while bulk posterior is well-behaved. Warmup slowness reflects expensive iterations in tails, not slow convergence.

**Diagnostic**: Run few warmup iterations and check acceptance probabilities and step sizes to gauge curvature problems.

## NUTS and Configuration

**No-U-Turn Sampler (NUTS)**: Automatically selects appropriate leapfrog step count per iteration, maximizing expected squared jump distance while avoiding random-walk behavior.

### Algorithm Details

NUTS generates proposals by:
1. Starting from current parameters
2. Drawing independent standard normal momentum vector
3. Evolving system forward and backward in time forming balanced binary tree
4. Increasing tree depth by one each iteration (doubling leapfrog steps)

**Termination**: Tree depth increases until either:
- U-turn criterion satisfied (or completed tree), or
- Maximum allowed depth reached

**Final Selection**: Parameter value selected via multinomial sampling, biased toward second half of trajectory (not standard Metropolis step).

**Output**: Reports `treedepth__` and `n_leapfrog__`:

2^(treedepth-1) - 1 < N_leapfrog <= 2^treedepth - 1

### NUTS Diagnostics

- **Tree depth = 0**: First leapfrog step immediately rejected, indicating extreme curvature, poorly-chosen step size
- **Tree depth = maximum**: Taking many leapfrog steps, terminated early. May indicate poor adaptation, very high target acceptance rate, or difficult posterior
- **Solution**: May require reparameterization or increased maximum depth

## Sampling Without Parameters

For forward data simulation (directed graphical models), no parameters needed:
- Don't declare parameters
- Model block can be omitted
- All outputs in generated quantities block

**Example**: Generate N binomial draws with K trials and success probability theta:

```stan
data {
  real<lower=0, upper=1> theta;
  int<lower=0> K;
  int<lower=0> N;
}
generated quantities {
  array[N] int<lower=0, upper=K> y;
  for (n in 1:N) {
    y[n] = binomial_rng(K, theta);
  }
}
```

**Configuration**: Use fixed-parameters setting (no adaptation needed). Set warmup iterations to zero.

## General Configuration Options

### Random Number Generator

Behavior determined by unsigned seed (positive integer). If unspecified or <= 0, system time generates seed. Seed always recorded in output.

**Chain Identifier**: Useful for multiple chains. Advances RNG large number of variates so different chain identifiers use non-overlapping subsequences.

**Reproducibility**: Complete reproducibility requires locking down: OS, compiler version, Stan version, all dependent libraries.

### Initialization

Initial parameter values either user-specified or randomly generated.

**User-defined**: Must satisfy declared constraints (constrained scale). Must specify all parameters or abort.

**Zero Initialization**: All variables initialized to zero on unconstrained scale. Transforms provide reasonable initializations:
- Unconstrained: 0
- Positive-constrained: 1
- [0,1]-constrained: 0.5
- Simplex: symmetric uniform
- Correlation/covariance: unit matrices

**Random Initialization**: Default draws from Uniform(-2, 2) on unconstrained scale. Alternatively specify different bounds. Results in ranges like:
- Unconstrained: (-2, 2)
- Positive-constrained: ~(0.14, 7.4)
- [0,1]-constrained: ~(0.12, 0.88)

## Divergent Transitions

HMC simulates particle trajectory in potential energy field (negative log posterior). Key feature: Hamiltonian conserved along trajectory. Leapfrog algorithm performs discretized first-order approximation.

**Divergence**: Occurs when simulated trajectory departs from true trajectory, measured by Hamiltonian departure from initial value. Threshold currently 10^3 (when working properly, divergences ~10^{-7}).

**Consequences**: Diverged positions never selected as next draw, reducing HMC to random walk, biasing estimates through incomplete posterior exploration.

**Primary Cause**: Highly curved posteriors requiring small step sizes. When step size too large relative to curvature, simulation diverges. When too small, inefficient, hitting maximum depth.

### Diagnosing and Eliminating Divergences

**Initial Steps**:
1. Lower initial step size
2. Increase target acceptance rate
3. Keep step size small enough for precision

**If insufficient**: Reparameterization required for manageable posterior curvature.

**Visualization**: Plot posterior draws highlighting divergent transitions to locate divergence origin. ShinyStan and RStan provide special plotting facilities.

## References

- Betancourt, Michael. 2016a. "Diagnosing Suboptimal Cotangent Disintegrations in Hamiltonian Monte Carlo." arXiv 1604.00695.
- Betancourt, Michael. 2016b. "Identifying the Optimal Integration Time in Hamiltonian Monte Carlo." arXiv 1601.00225.
- Betancourt, Michael. 2017. "A Conceptual Introduction to Hamiltonian Monte Carlo." arXiv 1701.02434.
- Betancourt, Michael, and Mark Girolami. 2013. "Hamiltonian Monte Carlo for Hierarchical Models." arXiv 1312.0906.
- Gelman, Andrew, et al. 2013. Bayesian Data Analysis. Third Edition. Chapman & Hall/CRC Press.
- Hoffman, Matthew D., and Andrew Gelman. 2014. "The No-U-Turn Sampler: Adaptively Setting Path Lengths in Hamiltonian Monte Carlo." Journal of Machine Learning Research 15: 1593-623.
- Leimkuhler, Benedict, and Sebastian Reich. 2004. Simulating Hamiltonian Dynamics. Cambridge University Press.
- Neal, Radford. 2011. "MCMC Using Hamiltonian Dynamics." In Handbook of Markov Chain Monte Carlo, 116-62.
- Nesterov, Y. 2009. "Primal-Dual Subgradient Methods for Convex Problems." Mathematical Programming 120(1): 221-59.
- Roberts, G. O., Andrew Gelman, and Walter G. Gilks. 1997. "Weak Convergence and Optimal Scaling of Random Walk Metropolis Algorithms." Annals of Applied Probability 7(1): 110-20.

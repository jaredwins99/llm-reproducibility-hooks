# Directions, Rotations, and Hyperspheres

## Overview

This Stan documentation section addresses directional statistics -- data and parameters constrained to represent directions. The fundamental challenge is that "spheres cannot be smoothly mapped to Euclidean space" since circular coordinates wrap (0 and 2pi represent the same point).

## Unit Vectors

Stan supports directional statistics through unit-vector parameters. A vector's length is calculated as:

||x|| = sqrt(x1^2 + x2^2 + ... + xK^2)

Declaration syntax:

```stan
unit_vector[K] x;
```

**Important note:** The system adds a Jacobian adjustment term to ensure proper probability distributions. This occurs because K-dimensional unit vectors have only K-1 degrees of freedom, yet "no continuous mapping exists between K-1 dimensions and R^n." Stan's approach applies standard normal distributions across K unconstrained variables, then projects them onto the hypersphere.

## Spheres and Manifolds

An n-sphere (S^n) comprises (n+1)-dimensional unit vectors. While existing in higher dimensions, S^n exhibits n-dimensional behavior locally. For example:

- S^1 (circle): 1D manifold in R^2
- S^2 (sphere): 2D manifold in R^3

These spaces are compact -- maximum distances between points exist -- unlike unbounded Euclidean spaces.

## Unconstrained Parameter Transformation

Points in R^K map to S^{K-1} via Muller's auxiliary variable method (1959):

x = y / sqrt(y^T y)

**Limitation:** This mapping remains undefined at zero, though this has measure zero during sampling. Unit vectors cannot initialize at zero; use small intervals around zero instead.

## Angles from Unit Vectors

Two-dimensional unit vectors convert to angles via arctangent:

```stan
parameters {
  unit_vector[2] xy;
}
transformed parameters {
  real<lower=-pi(), upper=pi()> theta = atan2(xy[2], xy[1]);
}
```

This approach prevents multimodal posteriors that explicit angle parameterization can produce.

## Temporal Applications

Circular representations naturally model periodic phenomena -- daily cycles use 24-hour clocks, annual progressions track seasonal patterns. These conventions "often arise by necessity" in practical applications and can incorporate ad-hoc adjustments for holidays or daylight variations.

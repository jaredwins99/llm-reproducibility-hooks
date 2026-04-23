"""Hierarchical linear regression task.

Ground-truth DGP:
  For group j, observation i:
    y[i,j] ~ Normal(beta0[j] + beta1[j] * x[i,j], sigma)
    beta0[j] ~ Normal(mu_b0, sigma_b0)
    beta1[j] ~ Normal(mu_b1, sigma_b1)
    x[i,j]   ~ Uniform(-2, 2)

Fixed DGP config below is load-bearing: changing any value invalidates prior runs.
Data is generated once at import time (seed=42), so all trials of this task see
the same data and the same ground truth.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer
from eval.tasks import register

DGP_CONFIG = dict(
    J=10, N_j=30,
    mu_b0=1.0, sigma_b0=0.5,
    mu_b1=0.8, sigma_b1=0.3,
    sigma=0.4,
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    J, N_j = c["J"], c["N_j"]
    N = J * N_j

    rng = np.random.RandomState(c["seed"])

    x_all = np.zeros(N)
    y_all = np.zeros(N)
    group_all = np.zeros(N, dtype=int)

    for j in range(J):
        beta0_j = rng.normal(c["mu_b0"], c["sigma_b0"])
        beta1_j = rng.normal(c["mu_b1"], c["sigma_b1"])
        x_j = rng.uniform(-2, 2, N_j)
        y_j = beta0_j + beta1_j * x_j + rng.normal(0, c["sigma"], N_j)

        start = j * N_j
        end = start + N_j
        x_all[start:end] = x_j
        y_all[start:end] = y_j
        group_all[start:end] = j + 1  # 1-indexed for Stan

    stan_data = {
        "N": N,
        "J": J,
        "group": group_all.tolist(),
        "x": x_all.tolist(),
        "y": y_all.tolist(),
    }
    true_params = {
        "mu_b0": c["mu_b0"],
        "sigma_b0": c["sigma_b0"],
        "mu_b1": c["mu_b1"],
        "sigma_b1": c["sigma_b1"],
        "sigma": c["sigma"],
    }
    return stan_data, true_params, y_all


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "intercept_pop": "population mean of group intercepts",
    "intercept_sd":  "sd of group intercepts",
    "slope_pop":     "population mean of group slopes",
    "slope_sd":      "sd of group slopes",
    "obs_sigma":     "observation noise sd",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "intercept_pop": _TRUE_PARAMS["mu_b0"],
    "intercept_sd":  _TRUE_PARAMS["sigma_b0"],
    "slope_pop":     _TRUE_PARAMS["mu_b1"],
    "slope_sd":      _TRUE_PARAMS["sigma_b1"],
    "obs_sigma":     _TRUE_PARAMS["sigma"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "intercept_pop": ["mu_b0", "mu_a", "alpha_pop", "mu_alpha", "intercept_pop"],
    "intercept_sd":  ["sigma_b0", "sigma_a", "sigma_alpha", "tau_alpha"],
    "slope_pop":     ["mu_b1", "mu_beta", "beta_pop", "mu_slope"],
    "slope_sd":      ["sigma_b1", "sigma_beta", "tau_beta", "sigma_slope"],
    "obs_sigma":     ["sigma", "sigma_y", "sigma_obs"],
}


def _build_scorer() -> StanScorer:
    return StanScorer(
        data=_STAN_DATA,
        true_params=ROLE_TRUE_VALUES,
        canonical_roles=CANONICAL_ROLES,
        fallback_map=FALLBACK_MAP,
        observed_y=_Y_OBS,
        is_zero_inflated=False,
        has_spatial=False,
        expected_artifacts=["simulate_data.py", "params.json"],
        n_warmup=500,
        n_sampling=500,
    )


_DATA_JSON = json.dumps(_STAN_DATA)


_PARAMS_JSON_INSTRUCTION = """

Also produce a params.json file in the current directory mapping these canonical roles to the Stan parameter names you used in your model. Only include roles that exist in your parameterization; omit any that don't apply.

Roles:
- "intercept_pop": population mean of group intercepts
- "intercept_sd":  sd of group intercepts
- "slope_pop":     population mean of group slopes
- "slope_sd":      sd of group slopes
- "obs_sigma":     observation noise sd

Format: a single JSON object. Example:
{"intercept_pop": "mu_b0", "intercept_sd": "sigma_b0", "slope_pop": "mu_b1", "slope_sd": "sigma_b1", "obs_sigma": "sigma"}"""


_MINIMAL_PROMPT = """Build a multilevel / hierarchical linear regression model in Stan with varying intercepts and slopes across J groups. Data in data.json has N, J, group[N] (1-indexed group index), x[N], y[N]. Save model.stan with a generated quantities y_rep block.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a multilevel hierarchical linear regression model in Stan with the following specification.

DATA (in data.json):
- N = total observations
- J = number of groups
- group[N]: 1-indexed group index for each observation
- x[N]: predictor
- y[N]: response

MODEL:
- y[i] ~ Normal(b0[group[i]] + b1[group[i]] * x[i], sigma)
- b0[j] ~ Normal(mu_b0, sigma_b0)  -- group intercepts
- b1[j] ~ Normal(mu_b1, sigma_b1)  -- group slopes

PARAMETERIZATION:
- Use a non-centered parameterization for b0[J] and b1[J].
- Use half-normal priors on sigma_b0, sigma_b1, and sigma.
- Use Normal priors with small sd on the population means mu_b0, mu_b1.

PARAMETER NAMES (required):
- mu_b0, sigma_b0, mu_b1, sigma_b1, sigma
- b0[J], b1[J] for the group-level intercepts and slopes

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.hierarchical_linear.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.hierarchical_linear.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

"""Gaussian Process regression task.

Ground-truth DGP:
  y[i] ~ Normal(f(x[i]), sigma)
  f ~ GP(0, K) with exponentiated-quadratic kernel:
    K[i,j] = magnitude^2 * exp(-0.5 * (x[i]-x[j])^2 / lengthscale^2)

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
    N=100,
    x_min=0.0,
    x_max=10.0,
    lengthscale=2.0,
    magnitude=1.5,
    obs_sigma=0.3,
    jitter=1e-6,
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    N = c["N"]
    lengthscale = c["lengthscale"]
    magnitude = c["magnitude"]
    sigma = c["obs_sigma"]

    rng = np.random.RandomState(c["seed"])
    x = np.linspace(c["x_min"], c["x_max"], N)

    diff = x[:, None] - x[None, :]
    K = (magnitude ** 2) * np.exp(-0.5 * (diff ** 2) / (lengthscale ** 2))
    K = K + c["jitter"] * np.eye(N)
    L = np.linalg.cholesky(K)

    eta = rng.normal(0.0, 1.0, N)
    f = L @ eta
    y = f + rng.normal(0.0, sigma, N)

    stan_data = {"N": N, "x": x.tolist(), "y": y.tolist()}
    true_params = {
        "lengthscale": lengthscale,
        "magnitude": magnitude,
        "obs_sigma": sigma,
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored parameters. Keys are the role names;
# values are one-line descriptions fed to the judge when it has to infer the
# role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "lengthscale": "GP kernel lengthscale (rho / ell / l) — controls smoothness",
    "magnitude":   "GP marginal standard deviation (alpha / sigma_f) — controls amplitude",
    "obs_sigma":   "Observation noise standard deviation (sigma)",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "lengthscale": _TRUE_PARAMS["lengthscale"],
    "magnitude":   _TRUE_PARAMS["magnitude"],
    "obs_sigma":   _TRUE_PARAMS["obs_sigma"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "lengthscale": ["rho", "ell", "l", "length_scale", "lengthscale"],
    "magnitude":   ["alpha", "sigma_f", "magnitude", "eta"],
    "obs_sigma":   ["sigma", "sigma_y", "sigma_obs", "noise_sd"],
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
- "lengthscale": GP kernel lengthscale (controls smoothness)
- "magnitude":   GP marginal standard deviation (controls amplitude)
- "obs_sigma":   observation noise standard deviation

Format: a single JSON object. Example:
{"lengthscale": "rho", "magnitude": "alpha", "obs_sigma": "sigma"}"""


_MINIMAL_PROMPT = """Build a Gaussian Process regression model in Stan.

Requirements:
- Standard GP with exponentiated-quadratic (squared exponential) kernel.
- The file data.json in the current directory contains: N (int), x (array[N]), y (array[N]).
- Save your Stan model to model.stan in the current directory.
- Include a generated quantities block producing y_rep for posterior predictive checks.
- You may also create simulate_data.py if you want to validate your approach against synthetic data.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a Gaussian Process regression model in Stan with the following specification.

DATA (in data.json):
- N = 100 observations
- x: length-N array of real-valued inputs on [0, 10]
- y: length-N array of real-valued outputs

MODEL:
- y[i] ~ Normal(f(x[i]), sigma)
- f ~ GP(0, K) with exponentiated-quadratic kernel:
    K[i,j] = alpha^2 * exp(-0.5 * (x[i]-x[j])^2 / rho^2)

PARAMETERIZATION:
- Use the non-centered Cholesky parameterization: f = L_K * eta with eta ~ std_normal().
- Add a small jitter (e.g. 1e-9) to the diagonal of K before cholesky_decompose.
- Parameter names: rho (lengthscale), alpha (magnitude), sigma (obs noise).

PRIORS:
- rho ~ inv_gamma(5, 5)
- alpha ~ std_normal() (constrained positive)
- sigma ~ std_normal() (constrained positive)

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.gp_regression.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.gp_regression.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

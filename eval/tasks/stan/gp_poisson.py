"""Spatial Gaussian Process Poisson regression task.

Ground-truth DGP:
  For location i in [0,10]^2:
    y[i] ~ Poisson(exp(f[i]))
    f ~ GP(intercept_mu, K)
    K[i,j] = magnitude^2 * exp(-0.5 * ||x[i]-x[j]||^2 / lengthscale^2)

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
    N=80, D=2,
    lengthscale=3.0,
    magnitude=0.8,
    intercept_mu=1.5,
    jitter=1e-6,
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    N, D = c["N"], c["D"]
    lengthscale = c["lengthscale"]
    magnitude = c["magnitude"]
    intercept_mu = c["intercept_mu"]

    rng = np.random.RandomState(c["seed"])
    x = rng.uniform(0, 10, (N, D))

    diff = x[:, None, :] - x[None, :, :]
    dist2 = np.sum(diff ** 2, axis=-1)
    K = magnitude ** 2 * np.exp(-0.5 * dist2 / lengthscale ** 2)
    K += c["jitter"] * np.eye(N)

    L = np.linalg.cholesky(K)
    eta = rng.normal(0, 1, N)
    f = intercept_mu + L @ eta

    rates = np.minimum(np.exp(f), 1e4)
    y = rng.poisson(rates)

    stan_data = {
        "N": N,
        "D": D,
        "x": x.tolist(),
        "y": y.astype(int).tolist(),
    }
    true_params = {
        "lengthscale": lengthscale,
        "magnitude": magnitude,
        "intercept_mu": intercept_mu,
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "lengthscale":  "GP kernel lengthscale",
    "magnitude":    "GP marginal standard deviation",
    "intercept_mu": "global intercept (log-rate mean)",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "lengthscale":  _TRUE_PARAMS["lengthscale"],
    "magnitude":    _TRUE_PARAMS["magnitude"],
    "intercept_mu": _TRUE_PARAMS["intercept_mu"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "lengthscale":  ["rho", "ell", "l", "length_scale"],
    "magnitude":    ["alpha", "sigma_f", "magnitude"],
    "intercept_mu": ["mu", "intercept", "a", "log_rate_mean", "global_mean"],
}


def _build_scorer() -> StanScorer:
    return StanScorer(
        data=_STAN_DATA,
        true_params=ROLE_TRUE_VALUES,
        canonical_roles=CANONICAL_ROLES,
        fallback_map=FALLBACK_MAP,
        observed_y=_Y_OBS,
        is_zero_inflated=False,
        has_spatial=True,
        expected_artifacts=["simulate_data.py", "params.json"],
        n_warmup=500,
        n_sampling=500,
    )


_DATA_JSON = json.dumps(_STAN_DATA)


_PARAMS_JSON_INSTRUCTION = """

Also produce a params.json file in the current directory mapping these canonical roles to the Stan parameter names you used in your model. Only include roles that exist in your parameterization; omit any that don't apply.

Roles:
- "lengthscale":  GP kernel lengthscale
- "magnitude":    GP marginal standard deviation
- "intercept_mu": global intercept (log-rate mean)

Format: a single JSON object. Example:
{"lengthscale": "rho", "magnitude": "alpha", "intercept_mu": "mu"}"""


_MINIMAL_PROMPT = """Build a Gaussian Process Poisson regression in Stan for count data on 2D locations. Data in data.json has N, D=2, x[N,D], y[N] (integer counts). Use exponentiated-quadratic kernel. Save to model.stan. Include generated quantities producing y_rep.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a Gaussian Process Poisson regression in Stan with the following specification.

DATA (in data.json):
- N = 80 observations
- D = 2 spatial dimensions
- x: array[N] vector[D] of locations in [0,10]^2
- y: length-N array of non-negative integer counts

MODEL:
- y[i] ~ Poisson(exp(f[i])), via poisson_log(f[i])
- f ~ GP(mu, K) with exponentiated-quadratic kernel:
    K[i,j] = alpha^2 * exp(-0.5 * ||x[i]-x[j]||^2 / rho^2)
- Use exact parameter names: rho (lengthscale), alpha (magnitude), mu (intercept).

PARAMETERIZATION:
- Non-centered Cholesky: f = mu + L * eta, with eta ~ std_normal() and L = cholesky_decompose(K + jitter*I).
- Priors: rho ~ inv_gamma(5, 5); alpha ~ std_normal(); mu ~ normal(0, 5).
- Likelihood: poisson_log(f).

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.gp_poisson.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.gp_poisson.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

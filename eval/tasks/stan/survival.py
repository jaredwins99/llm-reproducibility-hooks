"""Weibull survival regression with right-censoring task.

Ground-truth DGP:
  For subject i:
    T_latent[i] ~ Weibull(shape, scale_i)
    scale_i = exp(alpha + x1[i]*beta1 + x2[i]*beta2)
    T_obs[i] = min(T_latent[i], T_max)
    censored[i] = 1 if T_latent[i] > T_max

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
    N=150,
    K=2,
    T_max=3.0,
    alpha=0.5,
    beta1=0.3,
    beta2=-0.5,
    shape=1.5,
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, t_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    N, K, T_max = c["N"], c["K"], c["T_max"]
    alpha, beta1, beta2, shape = c["alpha"], c["beta1"], c["beta2"], c["shape"]

    rng = np.random.RandomState(c["seed"])
    x1 = rng.normal(0, 1, N)
    x2 = rng.normal(0, 1, N)
    scale = np.exp(alpha + x1 * beta1 + x2 * beta2)
    T_latent = rng.weibull(shape, N) * scale
    censored = (T_latent > T_max).astype(int)
    T_obs = np.minimum(T_latent, T_max)
    event = 1 - censored

    x = np.column_stack([x1, x2])
    stan_data = {
        "N": N,
        "K": K,
        "x": x.tolist(),
        "t": T_obs.tolist(),
        "event": event.astype(int).tolist(),
    }
    true_params = {
        "shape": shape,
        "alpha": alpha,
        "beta1": beta1,
        "beta2": beta2,
    }
    return stan_data, true_params, T_obs


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "shape":     "Weibull shape parameter (k/alpha/nu)",
    "intercept": "baseline log-scale coefficient",
    "slope1":    "coefficient on first covariate",
    "slope2":    "coefficient on second covariate",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "shape":     _TRUE_PARAMS["shape"],
    "intercept": _TRUE_PARAMS["alpha"],
    "slope1":    _TRUE_PARAMS["beta1"],
    "slope2":    _TRUE_PARAMS["beta2"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "shape":     ["shape", "k", "alpha", "nu", "weibull_shape"],
    "intercept": ["alpha", "beta0", "intercept", "mu", "log_scale_0"],
    "slope1":    ["beta1", "beta[1]", "coef[1]", "slope1"],
    "slope2":    ["beta2", "beta[2]", "coef[2]", "slope2"],
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
- "shape":     Weibull shape parameter (k/alpha/nu)
- "intercept": baseline log-scale coefficient
- "slope1":    coefficient on first covariate
- "slope2":    coefficient on second covariate

Format: a single JSON object. Example:
{"shape": "k", "intercept": "alpha", "slope1": "beta[1]", "slope2": "beta[2]"}"""


_MINIMAL_PROMPT = """Build a Weibull survival regression model in Stan with right-censoring. Data in data.json has N, K=2, x[N,K] (covariates), t[N] (observed times), event[N] (1 if uncensored, 0 if censored). Include both observed and censored contributions in the likelihood. Save model.stan. Include generated quantities y_rep.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a Weibull survival regression model in Stan with right-censoring.

DATA (in data.json):
- N = 150 subjects
- K = 2 covariates
- x: N×K matrix of covariates
- t: length-N vector of observed times (right-censored at T_max)
- event: length-N array of integers, 1 if event observed (uncensored), 0 if right-censored

MODEL:
- T_latent[i] ~ Weibull(shape, scale_i)
- scale_i = exp(alpha + x[i,1]*beta[1] + x[i,2]*beta[2])
- Likelihood splits by censoring status:
    for event[i] == 1 (uncensored): target += weibull_lpdf(t[i] | shape, scale_i)
    for event[i] == 0 (censored):   target += weibull_lccdf(t[i] | shape, scale_i)
- Use the Stan Weibull distribution (weibull_lpdf / weibull_lccdf), not a custom implementation.

PARAMETERS (use these exact names):
- real alpha          // intercept on log-scale
- vector[K] beta      // slope coefficients (so beta[1], beta[2])
- real<lower=0> shape // Weibull shape; you may name it `k` if preferred

PRIORS:
- alpha ~ normal(0, 5)
- beta ~ normal(0, 1)
- shape ~ normal(0, 2) with <lower=0> (half-normal)

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep (one replicated time per subject) for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.survival.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.survival.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

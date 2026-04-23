"""3-component Gaussian finite mixture task.

Ground-truth DGP:
  For i = 1..N:
    z[i] ~ Categorical(w)
    y[i] ~ Normal(mu[z[i]], sigma[z[i]])

Fixed DGP config below is load-bearing: changing any value invalidates prior runs.
Data is generated once at import time (seed=42), so all trials of this task see
the same data and the same ground truth.

NOTE: finite mixtures have label-switching. The scorer reports per-index recovery
only; component ordering differences inflate error. Accepted limitation.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer
from eval.tasks import register

DGP_CONFIG = dict(
    N=200,
    K=3,
    w=[0.3, 0.45, 0.25],
    mu=[-2.0, 1.0, 4.5],
    sigma=[0.5, 0.8, 0.6],
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    N, K = c["N"], c["K"]
    w = np.asarray(c["w"])
    mu = np.asarray(c["mu"])
    sigma = np.asarray(c["sigma"])

    rng = np.random.RandomState(c["seed"])
    z = rng.choice(K, N, p=w)
    y = rng.normal(mu[z], sigma[z])

    stan_data = {"N": N, "K": K, "y": y.tolist()}
    true_params = {
        "w": c["w"],
        "mu": c["mu"],
        "sigma": c["sigma"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "weights": "length-K mixture weights (simplex, sum to 1)",
    "means":   "length-K component means",
    "sds":     "length-K component standard deviations",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "weights": _TRUE_PARAMS["w"],
    "means":   _TRUE_PARAMS["mu"],
    "sds":     _TRUE_PARAMS["sigma"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "weights": ["w", "theta", "pi", "weights", "mixture_weights", "lambda"],
    "means":   ["mu", "means", "component_means", "m"],
    "sds":     ["sigma", "sd", "scales", "sds", "tau"],
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
- "weights": length-K mixture weights (simplex, sum to 1)
- "means":   length-K component means
- "sds":     length-K component standard deviations

Format: a single JSON object. Example:
{"weights": "w", "means": "mu", "sds": "sigma"}"""


_MINIMAL_PROMPT = """Build a finite Gaussian mixture model in Stan with K=3 components.

Requirements:
- The file data.json in the current directory contains your observed data with keys: N, K=3, y[N].
- Save your Stan model to model.stan in the current directory.
- Use log_sum_exp to marginalize the discrete component assignment.
- Generate y_rep in a generated quantities block.
- You may also create simulate_data.py if you want to validate your approach against synthetic data.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a finite Gaussian mixture model in Stan with K=3 components and the following specification.

DATA (in data.json):
- N = 200 observations
- K = 3 components
- y: length-N vector of real-valued observations

MODEL:
- y[i] ~ sum_{k=1..K} w[k] * Normal(mu[k], sigma[k])
- Marginalize the discrete component indicator using log_sum_exp in the likelihood.

PARAMETERIZATION:
- Mixture weights: simplex[K] w, with a Dirichlet(ones) prior.
- Component means: ordered[K] mu (enforces mu[1] < mu[2] < mu[3] for identifiability), with Normal priors.
- Component sds: half-Normal priors on sigma.
- Use parameter names: w, mu, sigma.

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.finite_mixture.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.finite_mixture.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

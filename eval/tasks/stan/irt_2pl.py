"""2-parameter logistic Item Response Theory task.

Ground-truth DGP:
  For person i, item j:
    y[i,j] ~ Bernoulli(inv_logit(alpha[j] * (theta[i] - beta[j])))
    theta[i] ~ Normal(0, 1)         -- person ability
    alpha[j] ~ LogNormal(0, 0.3)    -- item discrimination (positive)
    beta[j]  ~ Normal(0, 1)         -- item difficulty

Fixed DGP config below is load-bearing: changing any value invalidates prior runs.
Data is generated once at import time (seed=42), so all trials of this task see
the same data and the same ground truth.

Note: 2PL has identifiability issues (theta scale is arbitrary without constraint).
sigma_theta=1 is a standard constraint; the judge may map only what's identifiable
in Claude's model.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer
from eval.tasks import register

DGP_CONFIG = dict(
    I=50, J=20,
    mu_alpha_log=0.0, sigma_alpha_log=0.3,
    mu_beta=0.0, sigma_beta=1.0,
    sigma_theta=1.0,
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    I, J = c["I"], c["J"]

    rng = np.random.RandomState(c["seed"])
    theta = rng.normal(0.0, c["sigma_theta"], I)
    alpha = np.exp(rng.normal(c["mu_alpha_log"], c["sigma_alpha_log"], J))
    beta = rng.normal(c["mu_beta"], c["sigma_beta"], J)

    # Broadcast to I x J logit matrix, then flatten to long format.
    logit = alpha[None, :] * (theta[:, None] - beta[None, :])
    p = 1.0 / (1.0 + np.exp(-logit))
    y_mat = rng.binomial(1, p).astype(int)

    N = I * J
    person = np.repeat(np.arange(1, I + 1), J)  # 1-indexed
    item = np.tile(np.arange(1, J + 1), I)      # 1-indexed
    y = y_mat.reshape(N)

    stan_data = {
        "I": I,
        "J": J,
        "N": N,
        "person": person.tolist(),
        "item": item.tolist(),
        "y": y.tolist(),
    }
    true_params = {
        "mu_alpha_log": c["mu_alpha_log"],
        "sigma_alpha_log": c["sigma_alpha_log"],
        "mu_beta": c["mu_beta"],
        "sigma_beta": c["sigma_beta"],
        "sigma_theta": c["sigma_theta"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "mu_alpha_log":    "log-scale population mean of item discrimination",
    "sigma_alpha_log": "log-scale population sd of item discrimination",
    "mu_beta":         "population mean of item difficulty",
    "sigma_beta":      "population sd of item difficulty",
    "sigma_theta":     "sd of person ability (usually fixed to 1 for identifiability)",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "mu_alpha_log":    _TRUE_PARAMS["mu_alpha_log"],
    "sigma_alpha_log": _TRUE_PARAMS["sigma_alpha_log"],
    "mu_beta":         _TRUE_PARAMS["mu_beta"],
    "sigma_beta":      _TRUE_PARAMS["sigma_beta"],
    "sigma_theta":     _TRUE_PARAMS["sigma_theta"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "mu_alpha_log":    ["mu_log_alpha", "mu_a_log", "mu_log_disc", "log_alpha_pop"],
    "sigma_alpha_log": ["sigma_log_alpha", "sigma_a_log", "tau_log_alpha"],
    "mu_beta":         ["mu_beta", "mu_b", "mu_diff", "mu_difficulty"],
    "sigma_beta":      ["sigma_beta", "sigma_b", "sigma_difficulty", "tau_beta"],
    "sigma_theta":     ["sigma_theta", "sigma_ability", "tau_theta"],
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
- "mu_alpha_log":    log-scale population mean of item discrimination
- "sigma_alpha_log": log-scale population sd of item discrimination
- "mu_beta":         population mean of item difficulty
- "sigma_beta":      population sd of item difficulty
- "sigma_theta":     sd of person ability (usually fixed to 1 for identifiability)

Format: a single JSON object. Example:
{"mu_alpha_log": "mu_log_alpha", "sigma_alpha_log": "sigma_log_alpha", "mu_beta": "mu_beta", "sigma_beta": "sigma_beta", "sigma_theta": "sigma_theta"}"""


_MINIMAL_PROMPT = """Build a 2-parameter logistic (2PL) Item Response Theory model in Stan.

Data in data.json has I persons, J items, N=I*J responses in long format with person[N], item[N], y[N]. Save model.stan. Include generated quantities y_rep.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a 2-parameter logistic (2PL) Item Response Theory model in Stan with the following specification.

DATA (in data.json):
- I = 50 persons
- J = 20 items
- N = I*J = 1000 responses in long format
- person: array[N] of 1-indexed person ids
- item:   array[N] of 1-indexed item ids
- y:      array[N] of 0/1 responses

MODEL:
- y[n] ~ Bernoulli(inv_logit(alpha[item[n]] * (theta[person[n]] - beta[item[n]])))
- theta[i] ~ Normal(0, sigma_theta)   -- person ability
- alpha[j] ~ LogNormal(mu_log_alpha, sigma_log_alpha)  -- item discrimination (positive)
  (equivalently, log_alpha[j] ~ Normal(mu_log_alpha, sigma_log_alpha))
- beta[j]  ~ Normal(mu_beta, sigma_beta)  -- item difficulty

PARAMETERIZATION:
- Non-centered parameterization for theta and beta.
- LogNormal for alpha (or equivalently a normal on log_alpha / alpha_log).
- Standard_normal priors on hyperparameters where appropriate.
- Use exact parameter names: theta, alpha, beta, log_alpha (or alpha_log), mu_log_alpha, sigma_log_alpha, mu_beta, sigma_beta.
- Identifiability constraint: sigma_theta = 1 (fixed in the data block, not a parameter).

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.irt_2pl.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.irt_2pl.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

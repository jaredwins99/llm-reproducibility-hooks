"""Hidden Markov Model task (K=2 Gaussian emissions).

Ground-truth DGP:
  z[0] ~ Categorical(pi_init)
  z[t] | z[t-1]=k ~ Categorical(A[k, :])
  y[t] | z[t]=k  ~ Normal(mu[k], sigma[k])

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
    T=200,
    K=2,
    pi_init=[0.6, 0.4],
    A=[[0.85, 0.15], [0.25, 0.75]],
    mu=[0.0, 3.5],
    sigma=[0.5, 0.8],
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    T, K = c["T"], c["K"]
    pi_init = np.asarray(c["pi_init"])
    A = np.asarray(c["A"])
    mu = np.asarray(c["mu"])
    sigma = np.asarray(c["sigma"])

    rng = np.random.RandomState(c["seed"])
    z = np.zeros(T, dtype=int)
    y = np.zeros(T)

    z[0] = rng.choice(K, p=pi_init)
    y[0] = rng.normal(mu[z[0]], sigma[z[0]])
    for t in range(1, T):
        z[t] = rng.choice(K, p=A[z[t - 1]])
        y[t] = rng.normal(mu[z[t]], sigma[z[t]])

    stan_data = {"T": T, "K": K, "y": y.tolist()}
    true_params = {
        "trans_row1": float(A[0][0]),
        "trans_row2": float(A[1][1]),
        "emission_means": c["mu"],
        "emission_sds": c["sigma"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored parameters. Keys are the role names;
# values are one-line descriptions fed to the judge when it has to infer the
# role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "trans_row1":     "P(z_{t+1}=1 | z_t=1), the diagonal element A[1,1]",
    "trans_row2":     "P(z_{t+1}=2 | z_t=2), the diagonal element A[2,2]",
    "emission_means": "length-K vector of emission means",
    "emission_sds":   "length-K vector of emission sds",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "trans_row1":     _TRUE_PARAMS["trans_row1"],
    "trans_row2":     _TRUE_PARAMS["trans_row2"],
    "emission_means": _TRUE_PARAMS["emission_means"],
    "emission_sds":   _TRUE_PARAMS["emission_sds"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. The judge may use Stan indexing like A[1,1] directly.
FALLBACK_MAP = {
    "trans_row1":     ["A[1,1]", "p11", "stay1", "diag1"],
    "trans_row2":     ["A[2,2]", "p22", "stay2", "diag2"],
    "emission_means": ["mu", "means", "emission_mu", "m"],
    "emission_sds":   ["sigma", "sd", "emission_sigma", "scales"],
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
- "trans_row1":     P(z_{t+1}=1 | z_t=1), the diagonal element A[1,1]
- "trans_row2":     P(z_{t+1}=2 | z_t=2), the diagonal element A[2,2]
- "emission_means": length-K vector of emission means
- "emission_sds":   length-K vector of emission sds

Format: a single JSON object. Example:
{"trans_row1": "A[1,1]", "trans_row2": "A[2,2]", "emission_means": "mu", "emission_sds": "sigma"}"""


_MINIMAL_PROMPT = """Build a Hidden Markov Model in Stan with K=2 discrete latent states and Gaussian emissions.

Requirements:
- Marginalize over the discrete states via the forward algorithm (use log_sum_exp).
- The file data.json in the current directory contains your observed data with keys: T, K=2, y[T].
- Save your Stan model to model.stan in the current directory.
- Include a generated quantities block producing y_rep for posterior predictive checks.
- You may also create simulate_data.py if you want to validate your approach against synthetic data.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a Hidden Markov Model in Stan with K=2 discrete latent states and Gaussian emissions, following this specification.

DATA (in data.json):
- T = 200 timepoints
- K = 2 hidden states
- y: length-T vector of real-valued observations

MODEL:
- z[1] ~ Categorical(pi_init), z[t] | z[t-1]=k ~ Categorical(A[k, :])
- y[t] | z[t]=k ~ Normal(mu[k], sigma[k])
- Marginalize the discrete z[t] out via the forward algorithm using log_sum_exp.

PARAMETERIZATION (use these exact Stan names):
- `simplex[K] A[K]` — each row of the transition matrix is a simplex (row-stochastic).
- `simplex[K] pi_init` — initial state distribution.
- `ordered[K] mu` — emission means, ordered for identifiability.
- `vector<lower=0>[K] sigma` — emission sds, half-normal priors.

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.hmm.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.hmm.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

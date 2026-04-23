"""Multilevel zero-inflated INGARCH task.

Ground-truth DGP:
  For group g, time t:
    y[g,t] ~ ZI-Poisson(pi[g], lambda[g,t])
    lambda[g,t] = omega[g] + sum_p alpha[p]*y[g,t-p] + sum_q beta[q]*lambda[g,t-q]
    omega[g] ~ LogNormal(mu_omega, sigma_omega)
    pi[g]    = inv_logit(Normal(mu_pi_logit, sigma_pi_logit))

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
    G=8, T=300, P=7, Q=7, burn=50,
    mu_omega=1.5, sigma_omega=0.3,
    mu_pi_logit=-1.5, sigma_pi_logit=0.4,
    alpha=[0.08, 0.06, 0.04, 0.03, 0.02, 0.015, 0.01],
    beta=[0.10, 0.07, 0.05, 0.03, 0.02, 0.015, 0.01],
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    G, T, P, Q, burn = c["G"], c["T"], c["P"], c["Q"], c["burn"]
    alpha = np.asarray(c["alpha"])
    beta = np.asarray(c["beta"])

    rng = np.random.RandomState(c["seed"])
    assert alpha.sum() + beta.sum() < 1.0, "non-stationary DGP"

    omega = np.exp(rng.normal(c["mu_omega"], c["sigma_omega"], G))
    pi_logit = rng.normal(c["mu_pi_logit"], c["sigma_pi_logit"], G)
    pi = 1.0 / (1.0 + np.exp(-pi_logit))
    max_lag = max(P, Q)
    stationary_mean = omega / (1.0 - alpha.sum() - beta.sum())

    T_total = T + burn
    y = np.zeros((G, T_total), dtype=int)
    lam = np.zeros((G, T_total))

    for g in range(G):
        lam[g, :max_lag] = stationary_mean[g]
        for t in range(max_lag):
            y[g, t] = 0 if rng.random() < pi[g] else rng.poisson(max(lam[g, t], 0.01))

        for t in range(max_lag, T_total):
            contrib = omega[g]
            for p in range(P):
                contrib += alpha[p] * y[g, t - 1 - p]
            for q in range(Q):
                contrib += beta[q] * lam[g, t - 1 - q]
            lam[g, t] = max(contrib, 0.01)
            y[g, t] = 0 if rng.random() < pi[g] else rng.poisson(lam[g, t])

    y = y[:, burn:]
    stan_data = {"G": G, "T": T, "P": P, "Q": Q, "y": y.tolist()}
    true_params = {
        "mu_omega": c["mu_omega"],
        "sigma_omega": c["sigma_omega"],
        "mu_pi_logit": c["mu_pi_logit"],
        "sigma_pi_logit": c["sigma_pi_logit"],
        "alpha": c["alpha"],
        "beta": c["beta"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "intercept_pop":  "population mean of group intercepts (log scale) — LogNormal mu for omega",
    "intercept_sd":   "population sd of group intercepts (log scale) — LogNormal sigma for omega",
    "zi_pop":         "population mean of the zero-inflation logit across groups",
    "zi_sd":          "population sd of the zero-inflation logit across groups",
    "obs_lag":        "length-P vector of observation-lag coefficients (shared or population mean). Index i = lag i",
    "mean_lag":       "length-Q vector of conditional-mean-lag coefficients (shared or population mean). Index i = lag i",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "intercept_pop":  _TRUE_PARAMS["mu_omega"],
    "intercept_sd":   _TRUE_PARAMS["sigma_omega"],
    "zi_pop":         _TRUE_PARAMS["mu_pi_logit"],
    "zi_sd":          _TRUE_PARAMS["sigma_pi_logit"],
    "obs_lag":        _TRUE_PARAMS["alpha"],
    "mean_lag":       _TRUE_PARAMS["beta"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "intercept_pop":  ["mu_omega", "mu_alpha", "alpha_pop", "mu_intercept", "intercept_pop", "log_lambda_pop"],
    "intercept_sd":   ["sigma_omega", "sigma_alpha", "sigma_intercept"],
    "zi_pop":         ["mu_pi_logit", "mu_zi_logit", "mu_zi", "theta_pop", "zi_pop", "mu_theta"],
    "zi_sd":          ["sigma_pi_logit", "sigma_zi_logit", "sigma_zi", "sigma_theta"],
    "obs_lag":        ["alpha", "mu_beta", "beta_pop", "phi", "mu_phi", "obs_coef"],
    "mean_lag":       ["beta", "mu_gamma", "gamma_pop", "theta", "mu_theta", "mean_coef"],
}


def _build_scorer() -> StanScorer:
    return StanScorer(
        data=_STAN_DATA,
        true_params=ROLE_TRUE_VALUES,
        canonical_roles=CANONICAL_ROLES,
        fallback_map=FALLBACK_MAP,
        observed_y=_Y_OBS,
        is_zero_inflated=True,
        has_spatial=False,
        expected_artifacts=["simulate_data.py", "params.json"],
        n_warmup=500,
        n_sampling=500,
    )


_DATA_JSON = json.dumps(_STAN_DATA)


_PARAMS_JSON_INSTRUCTION = """

Also produce a params.json file in the current directory mapping these canonical roles to the Stan parameter names you used in your model. Only include roles that exist in your parameterization; omit any that don't apply.

Roles:
- "intercept_pop": population mean of group intercepts (log scale)
- "intercept_sd":  population sd of group intercepts (log scale)
- "zi_pop":        population mean of the zero-inflation logit
- "zi_sd":         population sd of the zero-inflation logit
- "obs_lag":       length-P vector of observation-lag coefficients (shared or population mean)
- "mean_lag":      length-Q vector of conditional-mean-lag coefficients (shared or population mean)

Format: a single JSON object. Example:
{"intercept_pop": "mu_alpha", "intercept_sd": "sigma_alpha", "zi_pop": "mu_zi_logit", "zi_sd": "sigma_zi", "obs_lag": "mu_beta", "mean_lag": "mu_gamma"}"""


_MINIMAL_PROMPT = """Build a multilevel zero-inflated INGARCH model in Stan.

Requirements:
- Hierarchical (multilevel) structure across groups.
- Zero-inflated count observations.
- INGARCH conditional mean with at least 7 observation lags and 7 conditional-mean lags.
- The file data.json in the current directory contains your observed data with keys: G, T, P, Q, y[G, T].
- Save your Stan model to model.stan in the current directory.
- You may also create simulate_data.py if you want to validate your approach against synthetic data.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a multilevel zero-inflated INGARCH(P,Q) model in Stan with the following specification.

DATA (in data.json):
- G = 8 groups
- T = 300 timepoints per group
- P = 7 observation lags
- Q = 7 conditional-mean lags
- y: G×T array of non-negative integer counts

MODEL:
- y[g,t] ~ ZI-Poisson(pi[g], lambda[g,t])
- lambda[g,t] = omega[g] + sum_{p=1..P} alpha[p] * y[g,t-p] + sum_{q=1..Q} beta[q] * lambda[g,t-q]
- omega[g] ~ LogNormal(mu_omega, sigma_omega)
- pi[g] = inv_logit(theta[g]) where theta[g] ~ Normal(mu_pi_logit, sigma_pi_logit)
- alpha and beta shared across groups for identifiability.

PARAMETERIZATION:
- Non-centered where appropriate.
- Ensure stationarity: sum(alpha) + sum(beta) < 1.
- Use weakly informative priors (not uniform).

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.ingarch.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.ingarch.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

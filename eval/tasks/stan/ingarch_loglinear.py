"""Multilevel zero-inflated INGARCH task — LOG-LINEAR DGP.

Complement to `ingarch.py` (which uses the additive DGP). This task's data is
generated from the log-linear Fokianos/Tjøstheim recursion:

  nu[g,t]     = alpha[g] + Σ_p β[p]·log(1 + y[g,t-p]) + Σ_q γ[q]·nu[g,t-q]
  lambda[g,t] = exp(nu[g,t])
  y[g,t]      ~ ZI-Poisson(pi[g], lambda[g,t])

  alpha[g] ~ Normal(mu_alpha, sigma_alpha)     (log-scale group intercept)
  pi[g]    = inv_logit(Normal(mu_zi, sigma_zi))

Purpose: the confound test. Pilot 1 showed ref-forcing pushes Claude toward
log-linear INGARCH. On pilot 1's additive DGP this hurt fit. If ref-forcing's
bias matches THIS log-linear DGP, ref-forcing should help on the minimal prompt.

Roles are shared with ingarch.py; canonical semantics don't change across DGPs.
Fit the data with whichever form Claude picks — the scorer checks per-role
recovery via the judge.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer
from eval.tasks import register
from eval.tasks.stan.ingarch import CANONICAL_ROLES, FALLBACK_MAP

DGP_CONFIG = dict(
    G=8, T=300, P=7, Q=7, burn=50,
    mu_alpha=1.0, sigma_alpha=0.3,           # exp(1.0)=2.7 baseline; modest group variation
    mu_zi_logit=-1.5, sigma_zi_logit=0.4,
    beta=[0.15, 0.10, 0.07, 0.05, 0.03, 0.02, 0.01],   # sum 0.43
    gamma=[0.10, 0.07, 0.05, 0.03, 0.02, 0.01, 0.01],  # sum 0.29 — stable recursion
    seed=42,
)


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    G, T, P, Q, burn = c["G"], c["T"], c["P"], c["Q"], c["burn"]
    beta = np.asarray(c["beta"])
    gamma = np.asarray(c["gamma"])
    assert beta.sum() + gamma.sum() < 1.0, "log-linear DGP not clearly stable"

    rng = np.random.RandomState(c["seed"])
    alpha = rng.normal(c["mu_alpha"], c["sigma_alpha"], G)
    zi_logit = rng.normal(c["mu_zi_logit"], c["sigma_zi_logit"], G)
    pi = 1.0 / (1.0 + np.exp(-zi_logit))
    max_lag = max(P, Q)
    T_total = T + burn

    nu = np.zeros((G, T_total))
    y = np.zeros((G, T_total), dtype=int)

    for g in range(G):
        nu[g, :max_lag] = alpha[g]
        for t in range(max_lag):
            lam = np.exp(min(nu[g, t], 20.0))  # cap exp to avoid overflow during warmup
            y[g, t] = 0 if rng.random() < pi[g] else rng.poisson(lam)

        for t in range(max_lag, T_total):
            eta = alpha[g]
            for p in range(P):
                eta += beta[p] * np.log1p(y[g, t - 1 - p])
            for q in range(Q):
                eta += gamma[q] * nu[g, t - 1 - q]
            # Soft cap to keep lambda numerically reasonable; doesn't affect the model
            # Claude sees, only the observed y values that result.
            eta = min(eta, 20.0)
            nu[g, t] = eta
            lam = np.exp(eta)
            y[g, t] = 0 if rng.random() < pi[g] else rng.poisson(lam)

    y = y[:, burn:]
    stan_data = {"G": G, "T": T, "P": P, "Q": Q, "y": y.tolist()}
    true_params = {
        "mu_alpha": c["mu_alpha"],
        "sigma_alpha": c["sigma_alpha"],
        "mu_zi_logit": c["mu_zi_logit"],
        "sigma_zi_logit": c["sigma_zi_logit"],
        "beta": c["beta"],
        "gamma": c["gamma"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Map role -> log-linear DGP true param name. Same roles as additive INGARCH,
# different DGP-side naming, same canonical semantics for the scorer.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "intercept_pop":  _TRUE_PARAMS["mu_alpha"],
    "intercept_sd":   _TRUE_PARAMS["sigma_alpha"],
    "zi_pop":         _TRUE_PARAMS["mu_zi_logit"],
    "zi_sd":          _TRUE_PARAMS["sigma_zi_logit"],
    "obs_lag":        _TRUE_PARAMS["beta"],
    "mean_lag":       _TRUE_PARAMS["gamma"],
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

Also produce a params.json file in the current directory mapping these canonical roles to the Stan parameter names you used in your model. Omit any role that doesn't apply to your parameterization.

Roles:
- "intercept_pop": population mean of group intercepts (log scale)
- "intercept_sd":  population sd of group intercepts (log scale)
- "zi_pop":        population mean of the zero-inflation logit
- "zi_sd":         population sd of the zero-inflation logit
- "obs_lag":       length-P vector of observation-lag coefficients (shared or population mean)
- "mean_lag":      length-Q vector of conditional-mean-lag coefficients (shared or population mean)

Format: a single JSON object. Example:
{"intercept_pop": "mu_alpha", "obs_lag": "beta", "mean_lag": "gamma"}"""


_MINIMAL_PROMPT = """Build a multilevel zero-inflated INGARCH model in Stan.

Requirements:
- Hierarchical (multilevel) structure across groups.
- Zero-inflated count observations.
- INGARCH conditional mean with at least 7 observation lags and 7 conditional-mean lags.
- The file data.json in the current directory contains your observed data with keys: G, T, P, Q, y[G, T].
- Save your Stan model to model.stan in the current directory.
- You may also create simulate_data.py if you want to validate your approach against synthetic data.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a multilevel zero-inflated LOG-LINEAR INGARCH(P,Q) model in Stan with the following specification.

DATA (in data.json):
- G = 8 groups
- T = 300 timepoints per group
- P = 7 observation lags
- Q = 7 conditional-mean lags
- y: G×T array of non-negative integer counts

MODEL (log-linear INGARCH, Fokianos/Tjøstheim form):
- y[g,t] ~ ZI-Poisson(pi[g], lambda[g,t])
- lambda[g,t] = exp(nu[g,t])
- nu[g,t] = alpha[g] + sum_{p=1..P} beta[p] * log(1 + y[g,t-p]) + sum_{q=1..Q} gamma[q] * nu[g,t-q]
- alpha[g] ~ Normal(mu_alpha, sigma_alpha)
- pi[g] = inv_logit(theta[g]) where theta[g] ~ Normal(mu_zi_logit, sigma_zi_logit)
- beta and gamma shared across groups for identifiability.

PARAMETERIZATION:
- Non-centered where appropriate.
- Ensure stability: sum(beta) + sum(gamma) < 1.
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

register(TaskSpec(id="stan.ingarch_loglinear.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.ingarch_loglinear.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

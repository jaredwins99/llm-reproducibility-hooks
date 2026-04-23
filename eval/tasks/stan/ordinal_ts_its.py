"""Ordinal mixed-effects time series with AR(1) errors, ITS, and heteroscedastic variance.

DGP: G groups x T time points, K=5 ordinal categories. Latent continuous
y*_gt = alpha[g] + beta*time + delta*post + tau[g]*post + eta[g,t]
with AR(1) errors eta and log-linear heteroscedastic innovation sd. Train =
first 30 timepoints per group, test = last 10.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    G=8, T_train=30, T_test=10, K=5,
    mu_alpha=0.0, sigma_alpha=0.4,
    beta=0.02, delta=0.5, sigma_tau=0.3,
    rho=0.5, sigma_eps=0.6, gamma=0.3,
    cutpoints=[-1.5, -0.5, 0.5, 1.5],
    intervention_t=20,  # 1-indexed: post=1 for t >= 20
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    G = c["G"]
    T_total = c["T_train"] + c["T_test"]
    K = c["K"]
    cutpoints = np.asarray(c["cutpoints"])

    alpha = rng.normal(c["mu_alpha"], c["sigma_alpha"], G)
    tau = rng.normal(0.0, c["sigma_tau"], G)

    time_mat = np.tile(np.arange(1, T_total + 1, dtype=float), (G, 1))
    post_mat = (time_mat >= c["intervention_t"]).astype(float)
    x_mat = rng.normal(0.0, 1.0, (G, T_total))

    eta = np.zeros((G, T_total))
    for g in range(G):
        eta[g, 0] = rng.normal(0.0, c["sigma_eps"] * np.exp(c["gamma"] * x_mat[g, 0]))
        for t in range(1, T_total):
            sd = c["sigma_eps"] * np.exp(c["gamma"] * x_mat[g, t])
            eta[g, t] = c["rho"] * eta[g, t - 1] + rng.normal(0.0, sd)

    y_star = (alpha[:, None]
              + c["beta"] * time_mat
              + c["delta"] * post_mat
              + tau[:, None] * post_mat
              + eta)

    # Ordinal discretization: y = k (1..K) if cutpoints[k-2] <= y* < cutpoints[k-1]
    # i.e. k = 1 + sum(y* >= cutpoints)
    y = 1 + np.sum(y_star[..., None] >= cutpoints[None, None, :], axis=-1)
    y = y.astype(int)

    T_train = c["T_train"]
    T_test = c["T_test"]

    return {
        "G": G,
        "T_train": T_train,
        "T_test": T_test,
        "K": K,
        "y_train": y[:, :T_train].tolist(),
        "x_train": x_mat[:, :T_train].tolist(),
        "post_train": post_mat[:, :T_train].tolist(),
        "time_train": time_mat[:, :T_train].tolist(),
        "y_test": y[:, T_train:].tolist(),
        "x_test": x_mat[:, T_train:].tolist(),
        "post_test": post_mat[:, T_train:].tolist(),
        "time_test": time_mat[:, T_train:].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (y_train, x_train, post_train, time_train, each shaped [G, T_train]) and a TEST set (y_test, x_test, post_test, time_test, each shaped [G, T_test]) of the same format. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute a flat vector of length G*T_test:

     vector[G * T_test] log_lik_test;
     // log_lik_test[(g-1)*T_test + t] = ordered_logistic_lpmf(y_test[g, t] | eta_test_gt, cutpoints)

where eta_test_gt is the latent linear predictor for group g at test time t under the current posterior draw.

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build an ordinal mixed-effects time series model in Stan. Outcome is a K=5 "
    "ordinal category per group per time; residuals are AR(1) autocorrelated "
    "within group; there's an interrupted time series intervention at t=20 with "
    "both fixed effect and group-specific intervention effects; residual variance "
    "may depend on a covariate (heteroscedastic)."
) + _ELPD_CLAUSE


_DETAILED_PROMPT = """Build an ordinal mixed-effects time series model in Stan with the following specification.

DATA (in data.json):
- G = 8 groups, T_train training timepoints per group, T_test test timepoints per group
- K = 5 ordinal categories
- y_train: array[G, T_train] of ints in 1..K
- x_train: matrix[G, T_train] — continuous covariate driving heteroscedasticity
- post_train: matrix[G, T_train] — indicator for post-intervention (1 if time >= 20, else 0)
- time_train: matrix[G, T_train] — time index (1..T_total)
- Same four fields with _test suffix.

MODEL (use these exact parameter names):
- Likelihood: y[g, t] ~ ordered_logistic(mu_gt, cutpoints)
  where mu_gt = alpha[g] + beta * time[g, t] + delta * post[g, t] + tau[g] * post[g, t] + eta[g, t]
- cutpoints: ordered[K-1], weakly informative prior
- alpha[g] ~ Normal(mu_alpha, sigma_alpha), non-centered
- tau[g] ~ Normal(0, sigma_tau), non-centered  (group-specific intervention effect)
- beta, delta: fixed effects, weakly informative priors
- AR(1) latent errors within group:
    eta[g, 1] ~ Normal(0, sigma_eps * exp(gamma * x[g, 1]))  (or stationary init)
    eta[g, t] = rho * eta[g, t-1] + epsilon[g, t],  epsilon[g, t] ~ Normal(0, sigma_eps * exp(gamma * x[g, t]))
- rho in (-1, 1); sigma_eps > 0; gamma real (log-linear heteroscedasticity)
- Use non-centered parameterizations for alpha and tau.
- Weakly informative priors on hyperparameters.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.ordinal_ts_its.minimal",
    prompt=_MINIMAL_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
    ),
    timeout_s=1800,
    expected_duration_s=300,
))

register(TaskSpec(
    id="stan.ordinal_ts_its.detailed",
    prompt=_DETAILED_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
    ),
    timeout_s=1800,
    expected_duration_s=300,
))

"""Change-point in a mixture of truncated Weibull regressions.

Composes three constructs: (1) unknown change-point in sequence,
(2) finite Weibull mixture within each regime, (3) right-truncation at t_max.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    N=200,
    tau_cp=110,
    t_max=6.0,
    w1=[0.7, 0.3],
    shapes1=[1.2, 2.0],
    alpha1=[0.3, 0.8],
    beta1=[0.2, -0.3],
    w2=[0.5, 0.5],
    shapes2=[1.5, 2.2],
    alpha2=[0.5, 1.0],
    beta2=[-0.1, 0.4],
    N_train=160,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    N = c["N"]
    tau = c["tau_cp"]
    t_max = c["t_max"]

    x = rng.normal(0.0, 1.0, N)
    y = np.zeros(N)

    # Rejection sampling for right-truncation at t_max.
    def draw(i, w, shapes, alpha, beta):
        while True:
            k = rng.choice(len(w), p=w)
            scale = np.exp(alpha[k] + beta[k] * x[i])
            t = scale * rng.weibull(shapes[k])
            if t < t_max:
                return t

    for i in range(N):
        if i < tau:
            y[i] = draw(i, c["w1"], c["shapes1"], c["alpha1"], c["beta1"])
        else:
            y[i] = draw(i, c["w2"], c["shapes2"], c["alpha2"], c["beta2"])

    N_train = c["N_train"]
    idx = np.arange(1, N + 1)  # 1-indexed sequence index

    return {
        "N_train": int(N_train),
        "N_test": int(N - N_train),
        "t_max": float(t_max),
        "y_train": y[:N_train].tolist(),
        "x_train": x[:N_train].tolist(),
        "idx_train": idx[:N_train].tolist(),
        "y_test": y[N_train:].tolist(),
        "x_test": x[N_train:].tolist(),
        "idx_test": idx[N_train:].tolist(),
        "N": int(N),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains a TRAINING set (N_train, y_train, x_train, idx_train) and a TEST set (N_test, y_test, x_test, idx_test) of the same format, plus N (total sequence length) and t_max (right-truncation bound). Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = <log density of y_test[i] given current parameters, x_test[i], idx_test[i]>;

   This log density must (a) account for right-truncation at t_max, and (b) marginalize over the regime (determined by whether idx_test[i] <= tau_cp) and over the mixture component.

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = "Build a model in Stan for a time-to-event outcome that has: (1) an unknown change-point in the generating process somewhere in the sequence, (2) a finite mixture of Weibull components within each regime, (3) right-truncation at t_max. Regressors affect the Weibull scales." + _ELPD_CLAUSE


_DETAILED_PROMPT = """Build a Stan model for a time-to-event outcome with a change-point, a Weibull mixture, and right-truncation.

DATA (in data.json):
- N: total sequence length
- t_max: right-truncation bound (all observations satisfy y < t_max)
- Training: N_train, y_train, x_train, idx_train (1-indexed sequence position in 1..N)
- Test: N_test, y_test, x_test, idx_test (parallel)

MODEL:
- Unknown change-point tau_cp in sequence index. Place a discrete uniform prior over tau_cp in {1, ..., N-1} and marginalize by summing the training log-likelihood over all candidate tau_cp locations (log_sum_exp over tau_cp_prob). A stick-breaking prior is also acceptable.
- Two regimes: observations with idx <= tau_cp are regime 1; idx > tau_cp are regime 2.
- Within each regime r in {1,2}: a K=2 Weibull mixture with mixture weights w1 (simplex[2]) and w2 (simplex[2]), shapes shape[2,K] (positive), and scales that depend on x:
    scale_{r,k,i} = exp(alpha[r,k] + beta[r,k] * x[i])
- Truncation: every observed Weibull log-density contribution must include the correction `-weibull_lccdf(t_max | shape, scale)` so the density integrates to 1 on [0, t_max).
- Mixture: within-regime log density at y[i] is `log_sum_exp_k( log(w_r[k]) + weibull_lpdf(y[i] | shape[r,k], scale_{r,k,i}) - weibull_lccdf(t_max | shape[r,k], scale_{r,k,i}) )`.

EXACT PARAMETER NAMES (please use these):
- tau_cp_prob: simplex of length N-1 (prior over change-point location), OR an equivalent explicit marginalization
- alpha: array[2] vector[K] or matrix[2,K]
- beta:  array[2] vector[K] or matrix[2,K]
- shape: array[2] vector<lower=0>[K] or matrix<lower=0>[2,K]
- w1, w2: simplex[K]

Weakly informative priors throughout.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.changepoint_weibull_mixture.minimal",
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
    id="stan.changepoint_weibull_mixture.detailed",
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

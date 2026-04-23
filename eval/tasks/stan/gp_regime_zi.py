"""Non-stationary Poisson with GP-smoothed log-intensity + regime switching + zero inflation.

Compositional ELPD task: the agent must jointly handle an HMM (marginalize over
discrete regime state), a latent GP on log-rate, and a zero-inflation mixture.
Train/test split is sequential: first 90 timepoints train, last 30 test.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    T=120,
    T_train=90,
    lengthscale=8.0,
    magnitude=0.6,
    offset=[0.0, 1.2],
    trans_11=0.95,
    trans_22=0.92,
    zi_prob=0.18,
    jitter=1e-6,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    T = c["T"]
    T_train = c["T_train"]
    T_test = T - T_train

    # GP on t = 1..T
    t = np.arange(1, T + 1, dtype=float)
    diff = t[:, None] - t[None, :]
    K = c["magnitude"] ** 2 * np.exp(-0.5 * diff ** 2 / c["lengthscale"] ** 2)
    K += c["jitter"] * np.eye(T)
    L = np.linalg.cholesky(K)
    f = L @ rng.normal(0, 1, T)

    # HMM regime path
    A = np.array([[c["trans_11"], 1 - c["trans_11"]],
                  [1 - c["trans_22"], c["trans_22"]]])
    z = np.zeros(T, dtype=int)
    z[0] = 0
    for i in range(1, T):
        z[i] = rng.choice(2, p=A[z[i - 1]])

    offset = np.array(c["offset"])
    eta = offset[z] + f

    # Observations with zero inflation
    pi = c["zi_prob"]
    y = np.zeros(T, dtype=int)
    for i in range(T):
        if rng.random() < pi:
            y[i] = 0
        else:
            rate = min(np.exp(eta[i]), 1e4)
            y[i] = rng.poisson(rate)

    return {
        "T_train": T_train,
        "T_test": T_test,
        "y_train": y[:T_train].astype(int).tolist(),
        "y_test": y[T_train:].astype(int).tolist(),
        "t_train": t[:T_train].tolist(),
        "t_test": t[T_train:].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains a TRAINING set (T_train, y_train, t_train) and a TEST set (T_test, y_test, t_test). The time indices t_train are 1..T_train and t_test are T_train+1..T_train+T_test — the test block is sequentially AFTER the train block. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[T_test] log_lik_test;
     for (i in 1:T_test)
       log_lik_test[i] = <log p(y_test[i] | parameters)>;

   where the density marginalizes over BOTH the unobserved regime state z_test[i] AND the zero-inflation component.

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = "Build a non-stationary Poisson model in Stan for a count time series with: (1) a latent continuous time-varying log-rate smoothed by a Gaussian process (exponentiated quadratic kernel), (2) a discrete binary regime-switching state that adds a regime-specific offset, (3) excess zeros (zero-inflation). Marginalize over both the regime state and the ZI component." + _ELPD_CLAUSE


_DETAILED_PROMPT = """Build a non-stationary Poisson time series model in Stan with the following specification.

DATA (in data.json):
- T_train training timepoints, T_test test timepoints (test block is sequentially AFTER train).
- y_train, y_test: non-negative integer counts.
- t_train, t_test: real-valued time indices (1..T_train and T_train+1..T_train+T_test).

MODEL:
- Latent GP f[t] over all T = T_train + T_test timepoints, with exponentiated-quadratic kernel:
    K[i,j] = alpha^2 * exp(-0.5 * (t[i] - t[j])^2 / rho^2)
  Use exp_quad_cov. Non-centered parameterization via Cholesky:
    f = L * eta_f, with eta_f ~ std_normal() and L = cholesky_decompose(K + jitter*I).
- Discrete binary regime state z[t] in {1,2}, a 2-state hidden Markov chain with
  transition matrix A (2x2), rows are simplexes. Use the forward algorithm to
  marginalize z for the training likelihood.
- Regime-specific log-intensity offset: offset[2] (a length-2 vector).
- Zero inflation with probability pi: each y[t] is 0 w.p. pi, else Poisson(exp(offset[z[t]] + f[t])).
  Handle the ZI mixture via log_sum_exp.

EXACT PARAMETER NAMES: rho (GP lengthscale), alpha (GP magnitude), A (2x2 with simplex rows), offset (length 2), pi (ZI probability).

PRIORS:
- rho ~ inv_gamma(5, 5)
- alpha ~ std_normal()
- eta_f ~ std_normal()
- offset ~ normal(0, 2)
- pi ~ beta(1, 1)
- A rows ~ dirichlet(...) (weakly informative)

TRAIN LIKELIHOOD:
- For t in 1..T_train, marginalize z via the forward algorithm. At each t, the
  per-regime emission log-density is the ZI Poisson:
    log_mix = log(pi + (1-pi) * exp(-lambda))  if y_t == 0
              log(1-pi) + poisson_log_lpmf(y_t | offset[k] + f[t]) otherwise
  where lambda = exp(offset[k] + f[t]). Implement with log_sum_exp for numerical safety.

TEST LOG-LIKELIHOOD:
- In generated quantities, compute log_lik_test[i] = log p(y_test[i] | parameters),
  marginalizing over both the regime state z_test[i] and the ZI component.
  You may compute the filtered regime distribution at the end of training and
  propagate it forward through A for the test window.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.gp_regime_zi.minimal",
    prompt=_MINIMAL_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
    ),
    timeout_s=1800,
    expected_duration_s=600,
))

register(TaskSpec(
    id="stan.gp_regime_zi.detailed",
    prompt=_DETAILED_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
    ),
    timeout_s=1800,
    expected_duration_s=600,
))

"""Latent Class Growth Mixture Model (LCGM) with covariate-dependent class
probabilities, within-class quadratic growth, and measurement error in a
level-2 covariate.

Composition: finite mixture over latent trajectory classes + multinomial
logit for class membership + quadratic growth within class + measurement
error submodel on a subject-level covariate. Held-out ELPD is computed
per test subject, marginalizing over the K latent classes.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    N_train=45, N_test=15, T=8, K=3,
    times=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
    beta0=[0.0, 1.5, -1.0],
    beta1=[0.3, 0.0, 0.6],
    beta2=[0.0, -0.1, -0.05],
    delta_2=0.8, delta_3=-0.6,
    sigma_y=0.3, sigma_me=0.25,
    seed=42,
)


def _softmax(v):
    v = np.asarray(v, dtype=float)
    v = v - v.max()
    e = np.exp(v)
    return e / e.sum()


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    N = c["N_train"] + c["N_test"]
    T = c["T"]
    times = np.array(c["times"], dtype=float)
    b0 = np.array(c["beta0"]); b1 = np.array(c["beta1"]); b2 = np.array(c["beta2"])

    true_x = rng.normal(0.0, 1.0, N)
    x_obs = true_x + rng.normal(0.0, c["sigma_me"], N)

    z = np.empty(N, dtype=int)
    for i in range(N):
        logits = np.array([0.0, c["delta_2"] * true_x[i], c["delta_3"] * true_x[i]])
        z[i] = rng.choice(c["K"], p=_softmax(logits))

    # Longitudinal observations
    subj_id = np.repeat(np.arange(1, N + 1), T)
    time_all = np.tile(times, N)
    y_all = np.empty(N * T)
    for i in range(N):
        k = z[i]
        mean_i = b0[k] + b1[k] * times + b2[k] * times ** 2
        y_all[i * T:(i + 1) * T] = mean_i + rng.normal(0.0, c["sigma_y"], T)

    N_train = c["N_train"]
    n_obs_train = N_train * T
    train_mask = subj_id <= N_train
    test_mask = ~train_mask

    # Re-index test subjects to 1..N_test
    subj_id_train = subj_id[train_mask].astype(int).tolist()
    subj_id_test = (subj_id[test_mask] - N_train).astype(int).tolist()

    return {
        "N_train": N_train,
        "N_test": c["N_test"],
        "T": T,
        "n_obs_train": int(n_obs_train),
        "n_obs_test": int(c["N_test"] * T),
        "subj_id_train": subj_id_train,
        "time_train": time_all[train_mask].tolist(),
        "y_train": y_all[train_mask].tolist(),
        "x_obs_train": x_obs[:N_train].tolist(),
        "subj_id_test": subj_id_test,
        "time_test": time_all[test_mask].tolist(),
        "y_test": y_all[test_mask].tolist(),
        "x_obs_test": x_obs[N_train:].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains a TRAINING set (N_train subjects, n_obs_train longitudinal rows with subj_id_train / time_train / y_train, and x_obs_train of length N_train) and a TEST set of the same format (N_test, n_obs_test, subj_id_test, time_test, y_test, x_obs_test). Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute a PER-SUBJECT held-out log density for each test subject, marginalizing over the K latent classes:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = log_sum_exp over k of
         ( log Pr(z=k | x_obs_test[i]) + sum_t log Normal(y_test[i, t] | class-k quadratic mean at time_test, sigma_y) );

   That is, log_lik_test[i] is the log marginal density of ALL T longitudinal observations for test subject i under the fitted model, integrating out the discrete class.

Your model will be scored by held-out ELPD: sum over test subjects of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a latent class growth mixture model (LCGM) in Stan: subjects belong to one of K=3 latent classes, each class has its own quadratic growth trajectory in time, and class membership probability depends on a subject-level covariate measured with error. Marginalize over discrete class assignment."
    + _ELPD_CLAUSE
)

_DETAILED_PROMPT = """Build a latent class growth mixture model (LCGM) in Stan with the following specification.

DATA (in data.json):
- N_train, N_test subjects; T = 8 longitudinal measurements per subject.
- Long-format training rows: subj_id_train[n_obs_train] (1-indexed into 1..N_train), time_train[n_obs_train], y_train[n_obs_train]. n_obs_train = N_train * T.
- x_obs_train[N_train]: subject-level covariate, measured with error.
- Test set has the same structure (subj_id_test is 1-indexed into 1..N_test).

MODEL:
- K = 3 latent trajectory classes (pin K=3, do not infer it).
- Class membership for subject i: z_i ~ Categorical(softmax([0, delta[1] * true_x_i, delta[2] * true_x_i])) — reference class 1, so delta is length 2.
- Measurement-error submodel: true_x[i] ~ Normal(0, 1); x_obs_train[i] ~ Normal(true_x[i], sigma_me). true_x is a latent parameter.
- Within-class quadratic growth: y_{i,t} | z_i=k ~ Normal(beta0[k] + beta1[k] * t + beta2[k] * t^2, sigma_y). Homoscedastic residuals across classes.
- Marginalize the discrete z out of the likelihood with log_sum_exp.
- Identifiability: constrain beta1 to be ordered[K] (slope-based ordering), OR equivalently order beta0. Pick one and stick with it.
- Non-centered parameterization where applicable.
- Weakly informative priors on beta0, beta1, beta2, delta, sigma_y, sigma_me.

Exact parameter names: beta0, beta1, beta2, delta, sigma_y, sigma_me, true_x.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.lcgm.minimal",
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
    id="stan.lcgm.detailed",
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

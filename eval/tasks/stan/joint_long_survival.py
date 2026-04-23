"""Joint longitudinal-survival model with competing risks, shared random
effects, and measurement error. ELPD scored on held-out subjects."""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register
from eval.tasks.stan.hier_linear_elpd import _ELPD_CLAUSE

DGP_CONFIG = dict(
    N=80, N_train=60, max_obs=6, t_max_long=5.0, t_admin=10.0,
    mu_b0=1.0, sigma_b0=0.7,
    mu_b1=0.5, sigma_b1=0.4,
    sigma_eps=0.3, sigma_me=0.3,
    lambda0_1=0.15, lambda0_2=0.10,
    gamma_1=0.8, gamma_2=-0.5,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    N = c["N"]

    # Subject-level random effects
    b0 = rng.normal(c["mu_b0"], c["sigma_b0"], N)
    b1 = rng.normal(c["mu_b1"], c["sigma_b1"], N)

    # Competing-risk latent event times: exponential w/ hazard lambda0_k * exp(gamma_k * b1[i])
    h1 = c["lambda0_1"] * np.exp(c["gamma_1"] * b1)
    h2 = c["lambda0_2"] * np.exp(c["gamma_2"] * b1)
    t1 = rng.exponential(1.0 / h1)
    t2 = rng.exponential(1.0 / h2)
    t_event_latent = np.minimum(t1, t2)
    type_latent = np.where(t1 <= t2, 1, 2)

    # Administrative censoring at t_admin
    censored = t_event_latent > c["t_admin"]
    event_time = np.where(censored, c["t_admin"], t_event_latent)
    event_type = np.where(censored, 0, type_latent).astype(int)

    # Longitudinal measurements: irregular times in [0, min(t_max_long, event_time)]
    subj_ids, times, y_obs = [], [], []
    for i in range(N):
        n_i = rng.randint(2, c["max_obs"] + 1)  # 2..6 observations
        t_upper = min(c["t_max_long"], event_time[i])
        if t_upper <= 0:
            continue
        t_i = np.sort(rng.uniform(0, t_upper, n_i))
        y_true = b0[i] + b1[i] * t_i + rng.normal(0, c["sigma_eps"], n_i)
        y_meas = y_true + rng.normal(0, c["sigma_me"], n_i)
        subj_ids.extend([i] * n_i)
        times.extend(t_i.tolist())
        y_obs.extend(y_meas.tolist())

    subj_ids = np.array(subj_ids, dtype=int)
    times = np.array(times)
    y_obs = np.array(y_obs)

    # Train/test split: first N_train subjects train, rest test
    N_train = c["N_train"]
    tr_mask = subj_ids < N_train
    te_mask = ~tr_mask

    # Re-index subjects within each split to be 1..N_train / 1..N_test
    train_subj = (subj_ids[tr_mask] + 1).tolist()  # 1..N_train
    test_subj = (subj_ids[te_mask] - N_train + 1).tolist()  # 1..N_test

    return {
        "N_train": int(N_train),
        "N_test": int(N - N_train),
        "n_obs_train": int(tr_mask.sum()),
        "subj_id_train": train_subj,
        "time_train": times[tr_mask].tolist(),
        "y_obs_train": y_obs[tr_mask].tolist(),
        "n_obs_test": int(te_mask.sum()),
        "subj_id_test": test_subj,
        "time_test": times[te_mask].tolist(),
        "y_obs_test": y_obs[te_mask].tolist(),
        "event_time_train": event_time[:N_train].tolist(),
        "event_type_train": event_type[:N_train].tolist(),
        "event_time_test": event_time[N_train:].tolist(),
        "event_type_test": event_type[N_train:].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)


_MINIMAL_PROMPT = (
    "Build a joint longitudinal-survival model in Stan with competing risks. "
    "The longitudinal outcome is measured with error and has subject-specific "
    "intercepts and slopes. The survival piece has two competing event types "
    "whose hazards depend on the subject's random slope (shared random effect). "
    "data.json has the training and test data in parallel structure."
    + _ELPD_CLAUSE
)


_DETAILED_PROMPT = """Build a joint longitudinal-survival model in Stan with competing risks and a shared random effect.

DATA (data.json) — parallel train/test structure:
- N_train, N_test: number of subjects in each split
- Longitudinal (one row per measurement):
  - n_obs_train, subj_id_train[n_obs_train] (1-indexed within split), time_train[n_obs_train], y_obs_train[n_obs_train]
  - Same with _test suffix
- Survival (one row per subject):
  - event_time_train[N_train], event_type_train[N_train] where 0 = censored, 1 or 2 = which competing event fired
  - Same with _test suffix

MODEL:
- Subject random effects (non-centered):
    b0[i] = mu_b0 + sigma_b0 * z0[i],  z0[i] ~ Normal(0,1)
    b1[i] = mu_b1 + sigma_b1 * z1[i],  z1[i] ~ Normal(0,1)
- Longitudinal with measurement error:
    true latent trajectory: eta_ij = b0[subj] + b1[subj] * time_ij
    y_obs_ij ~ Normal(eta_ij, sqrt(sigma_eps^2 + sigma_me^2))
    (equivalently, integrate out the per-observation noise; a single Normal with combined SD is fine.)
- Competing-risk survival with shared random slope:
    hazard_k[i](t) = lambda0[k] * exp(gamma[k] * b1[i])     for k in {1,2}
    Use constant baseline hazards (exponential event times) OR a Weibull baseline — constant is fine and matches the DGP.
    For subject i with event_type == k at time t: log-contribution =
        log(lambda0[k]) + gamma[k]*b1[i]  -  (lambda0[1]*exp(gamma[1]*b1[i]) + lambda0[2]*exp(gamma[2]*b1[i])) * t
    For censored subject (event_type == 0) at time t:
        -(lambda0[1]*exp(gamma[1]*b1[i]) + lambda0[2]*exp(gamma[2]*b1[i])) * t

PARAMETER NAMES (exact):
  mu_b0, sigma_b0, mu_b1, sigma_b1, sigma_eps, sigma_me,
  vector[2] lambda0,  vector[2] gamma
Use weakly informative priors.
""" + _ELPD_CLAUSE


# Override the ELPD clause wording to match the joint log_lik_test contract.
# We append an extra paragraph clarifying the contract for this task.
_LOG_LIK_CONTRACT = """

LOG_LIK CONTRACT FOR THIS TASK (overrides the generic vector[N_test] above):

In `generated quantities`, declare:

    vector[n_obs_test + N_test] log_lik_test;

- For i in 1:n_obs_test:
    log_lik_test[i] = normal_lpdf(y_obs_test[i] | b0_test[subj_id_test[i]] + b1_test[subj_id_test[i]] * time_test[i],
                                   sqrt(sigma_eps^2 + sigma_me^2));
  where b0_test, b1_test are draws of the test-subject random effects from their population prior
  (mu_b0, sigma_b0, mu_b1, sigma_b1) — these are NEW subjects, so integrate over the random-effect
  population by sampling/marginalizing b0_test, b1_test in generated quantities.
- For j in 1:N_test, log_lik_test[n_obs_test + j] = log density of (event_time_test[j], event_type_test[j])
  under the competing-risk model using that subject's sampled b1_test.

Held-out ELPD sums over all (n_obs_test + N_test) entries."""


_MINIMAL_PROMPT = _MINIMAL_PROMPT + _LOG_LIK_CONTRACT
_DETAILED_PROMPT = _DETAILED_PROMPT + _LOG_LIK_CONTRACT


register(TaskSpec(
    id="stan.joint_long_survival.minimal",
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
    id="stan.joint_long_survival.detailed",
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

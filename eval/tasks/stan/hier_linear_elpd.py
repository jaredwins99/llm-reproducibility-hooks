"""Shakedown task: hierarchical linear regression with held-out ELPD.

This is a simple task designed to validate the ELPD scoring pipeline
end-to-end. The DGP is easy (Claude will nail it), but the point here is
to confirm the train/test split + log_lik_test generated-quantities
contract works before we commit to harder compositional tasks.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer, DEFAULT_JUDGE_RUBRIC
from eval.tasks import register

DGP_CONFIG = dict(
    J=10, N_j_train=24, N_j_test=6,  # 240 train, 60 test
    mu_b0=1.0, sigma_b0=0.5,
    mu_b1=0.8, sigma_b1=0.3,
    sigma_obs=0.4,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    J = c["J"]
    N_j_train, N_j_test = c["N_j_train"], c["N_j_test"]

    y_train, x_train, group_train = [], [], []
    y_test, x_test, group_test = [], [], []

    for j in range(J):
        b0 = rng.normal(c["mu_b0"], c["sigma_b0"])
        b1 = rng.normal(c["mu_b1"], c["sigma_b1"])
        # Train observations for group j
        x_tr = rng.uniform(-2, 2, N_j_train)
        y_tr = b0 + b1 * x_tr + rng.normal(0, c["sigma_obs"], N_j_train)
        x_train.extend(x_tr.tolist())
        y_train.extend(y_tr.tolist())
        group_train.extend([j + 1] * N_j_train)
        # Test observations for group j
        x_te = rng.uniform(-2, 2, N_j_test)
        y_te = b0 + b1 * x_te + rng.normal(0, c["sigma_obs"], N_j_test)
        x_test.extend(x_te.tolist())
        y_test.extend(y_te.tolist())
        group_test.extend([j + 1] * N_j_test)

    return {
        "N_train": len(y_train),
        "J": J,
        "group_train": group_train,
        "x_train": x_train,
        "y_train": y_train,
        "N_test": len(y_test),
        "group_test": group_test,
        "x_test": x_test,
        "y_test": y_test,
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (N_train, y_train, x_train, group_train) and a TEST set (N_test, y_test, x_test, group_test) of the same format. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = <log density of y_test[i] given current parameters and x_test[i], group_test[i]>;

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = "Build a hierarchical (multilevel) linear regression model in Stan with varying intercepts AND varying slopes across J groups." + _ELPD_CLAUSE

_DETAILED_PROMPT = """Build a hierarchical linear regression model in Stan with the following specification.

DATA (in data.json):
- J = 10 groups
- N_train training observations, N_test test observations (single group_train/test index per row, 1-indexed)
- x_train, x_test: continuous covariate
- y_train, y_test: continuous outcome

MODEL:
- y[i] ~ Normal(b0[group[i]] + b1[group[i]] * x[i], sigma)
- b0[j] ~ Normal(mu_b0, sigma_b0)
- b1[j] ~ Normal(mu_b1, sigma_b1)
- Non-centered parameterization for b0 and b1.
- Weakly informative priors.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.hier_linear_elpd.minimal",
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
    id="stan.hier_linear_elpd.detailed",
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

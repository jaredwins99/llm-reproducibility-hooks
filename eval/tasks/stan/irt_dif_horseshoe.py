"""Hierarchical 2PL IRT with group-level DIF + horseshoe prior on DIF parameters.

DGP:
  y[i, j] ~ Bernoulli(inv_logit(alpha[j] * (theta[i] - beta[j] - dif[j, g[i]])))
    theta[i] ~ Normal(0, 1)                  person ability
    alpha[j] ~ LogNormal(0, 0.3)             item discrimination
    beta[j]  ~ Normal(0, 1)                  baseline difficulty
    dif[j, g]: sparse item-by-group offset; 4 of 20 items have true DIF
               drawn ~ Normal(0, 0.8); remaining 16 items have dif = 0.
               Group 1 is the reference (dif[:, 0] = 0).

20% of (person, item) pairs are held out for test. Scored by held-out ELPD.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    I=80, G=4, J=20,
    n_dif_items=4,
    sigma_dif=0.8,
    mu_alpha_log=0.0, sigma_alpha_log=0.3,
    sigma_beta=1.0,
    sigma_theta=1.0,
    test_frac=0.2,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    I, G, J = c["I"], c["G"], c["J"]
    rng = np.random.RandomState(c["seed"])

    # Persons split evenly across groups (1-indexed).
    assert I % G == 0, "I must be divisible by G for even split"
    per_group = I // G
    person_group = np.repeat(np.arange(1, G + 1), per_group)  # 1-indexed

    theta = rng.normal(0.0, c["sigma_theta"], I)
    alpha = np.exp(rng.normal(c["mu_alpha_log"], c["sigma_alpha_log"], J))
    beta = rng.normal(0.0, c["sigma_beta"], J)

    # DIF: only n_dif_items items have true DIF; group 1 (index 0) is reference.
    dif = np.zeros((J, G))
    dif_items = rng.choice(J, size=c["n_dif_items"], replace=False)
    for j in dif_items:
        # groups 2..G get nonzero DIF
        dif[j, 1:] = rng.normal(0.0, c["sigma_dif"], G - 1)

    # Generate full I x J response matrix.
    g_idx = person_group - 1  # 0-indexed for numpy
    # logit[i, j] = alpha[j] * (theta[i] - beta[j] - dif[j, g_idx[i]])
    dif_ij = dif[np.arange(J)[None, :], g_idx[:, None]]  # shape (I, J)
    logit = alpha[None, :] * (theta[:, None] - beta[None, :] - dif_ij)
    p = 1.0 / (1.0 + np.exp(-logit))
    y_mat = rng.binomial(1, p).astype(int)

    # Long format: N = I * J entries, then split 80/20.
    N = I * J
    person_all = np.repeat(np.arange(1, I + 1), J)  # 1-indexed
    item_all = np.tile(np.arange(1, J + 1), I)      # 1-indexed
    y_all = y_mat.reshape(N)

    idx = rng.permutation(N)
    n_test = int(round(c["test_frac"] * N))
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]

    return {
        "I": I,
        "J": J,
        "G": G,
        "person_group": person_group.tolist(),
        "n_train": int(len(train_idx)),
        "person_train": person_all[train_idx].tolist(),
        "item_train": item_all[train_idx].tolist(),
        "y_train": y_all[train_idx].tolist(),
        "n_test": int(len(test_idx)),
        "person_test": person_all[test_idx].tolist(),
        "item_test": item_all[test_idx].tolist(),
        "y_test": y_all[test_idx].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)


_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (n_train, person_train, item_train, y_train) and a TEST set (n_test, person_test, item_test, y_test) of the same format. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[n_test] log_lik_test;
     for (i in 1:n_test)
       log_lik_test[i] = <log Bernoulli density of y_test[i] given current parameters, person_test[i], item_test[i], and person_group[person_test[i]]>;

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a hierarchical 2PL Item Response Theory model in Stan with "
    "differential item functioning (DIF): each item may have a group-specific "
    "difficulty shift. Use sparsity-inducing (horseshoe) priors on the DIF "
    "parameters since most items should not show DIF. Persons are nested in "
    "groups."
    + _ELPD_CLAUSE
)


_DETAILED_PROMPT = """Build a hierarchical 2PL Item Response Theory model in Stan with differential item functioning (DIF), regularized by a horseshoe prior.

DATA (in data.json):
- I = 80 persons, J = 20 items, G = 4 groups
- person_group[I]: 1-indexed group id for each person
- Training set: n_train, person_train[n_train], item_train[n_train], y_train[n_train] (0/1)
- Test set:     n_test,  person_test[n_test],  item_test[n_test],  y_test[n_test]

MODEL:
- y[n] ~ Bernoulli(inv_logit(alpha[item[n]] * (theta[person[n]] - beta[item[n]] - dif[item[n], person_group[person[n]]])))
- theta[i] ~ Normal(0, 1)                    person ability; non-centered
- alpha[j] ~ LogNormal(0, 0.3)               item discrimination (or normal prior on log_alpha)
- beta[j]  ~ Normal(0, 1)                    baseline item difficulty; non-centered
- dif[j, g] for g in 2..G:  horseshoe prior
    dif[j, g] ~ Normal(0, tau * lambda[j, g])
    lambda[j, g] ~ HalfCauchy(0, 1)
    tau        ~ HalfCauchy(0, 1)
  For identifiability, FIX dif[j, 1] = 0 for all j (group 1 is the reference group).

PARAMETERIZATION:
- Non-centered parameterization for theta and beta.
- LogNormal for alpha (or equivalently a normal on log_alpha).
- Use exact parameter names: theta, alpha, beta, dif, tau, lambda.

""" + _ELPD_CLAUSE


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
    ),
    timeout_s=1800,
    expected_duration_s=600,
)


register(TaskSpec(id="stan.irt_dif_horseshoe.minimal",  prompt=_MINIMAL_PROMPT,  **_COMMON))
register(TaskSpec(id="stan.irt_dif_horseshoe.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

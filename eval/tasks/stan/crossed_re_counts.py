"""Crossed (non-nested) random effects NB count model with ME and MAR missingness.

Species x site crossed design, negative binomial overdispersion, covariate
measured with error, 20% MAR missing cells. Held-out ELPD scoring.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    N_species=20,
    N_sites=15,
    alpha=1.5,
    beta=0.4,
    sigma_species=0.6,
    sigma_site=0.3,
    phi=1.2,
    sigma_me=0.3,
    miss_frac=0.20,
    n_train=190,
    n_test=50,
    seed=42,
)


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    N_species, N_sites = c["N_species"], c["N_sites"]

    u_species = rng.normal(0, c["sigma_species"], N_species)
    v_site = rng.normal(0, c["sigma_site"], N_sites)

    # Full grid
    species_idx, site_idx, true_env, x_obs, y = [], [], [], [], []
    for s in range(N_species):
        for l in range(N_sites):
            te = rng.normal(0.0, 1.0)
            xo = te + rng.normal(0.0, c["sigma_me"])
            mu = np.exp(c["alpha"] + u_species[s] + v_site[l] + c["beta"] * te)
            # NB2 with mean mu and dispersion phi: var = mu + mu^2/phi
            p = c["phi"] / (c["phi"] + mu)
            yi = rng.negative_binomial(c["phi"], p)
            species_idx.append(s + 1)
            site_idx.append(l + 1)
            true_env.append(te)
            x_obs.append(xo)
            y.append(int(yi))

    N_full = len(y)
    # MAR: drop exactly 20% at random (60 of 300)
    n_miss = int(round(c["miss_frac"] * N_full))
    perm = rng.permutation(N_full)
    kept = perm[n_miss:]
    rng.shuffle(kept)

    n_train, n_test = c["n_train"], c["n_test"]
    assert len(kept) >= n_train + n_test, f"only {len(kept)} observed, need {n_train + n_test}"
    train_idx = kept[:n_train]
    test_idx = kept[n_train:n_train + n_test]

    def take(arr, idx):
        return [arr[i] for i in idx]

    return {
        "N_species": N_species,
        "N_sites": N_sites,
        "N_train": n_train,
        "N_test": n_test,
        "species_train": take(species_idx, train_idx),
        "site_train": take(site_idx, train_idx),
        "x_train_obs": take(x_obs, train_idx),
        "y_train": take(y, train_idx),
        "species_test": take(species_idx, test_idx),
        "site_test": take(site_idx, test_idx),
        "x_test_obs": take(x_obs, test_idx),
        "y_test": take(y, test_idx),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (N_train, y_train, species_train, site_train, x_train_obs) and a TEST set (N_test, y_test, species_test, site_test, x_test_obs) of the same format. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = neg_binomial_2_lpmf(y_test[i] | mu_test_i, phi);

   where mu_test_i = exp(alpha + u_species[species_test[i]] + v_site[site_test[i]] + beta * x_test_obs[i]).

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = "Build a crossed random-effects count model in Stan with non-nested species and site effects, overdispersion (negative binomial), and a covariate measured with error. Some grid cells are missing at random." + _ELPD_CLAUSE

_DETAILED_PROMPT = """Build a crossed (non-nested) random-effects negative binomial count model in Stan with the following specification.

DATA (in data.json):
- N_species = 20 species, N_sites = 15 sites (non-nested — species crossed with sites).
- N_train training observations, N_test test observations.
- species_train[N_train], site_train[N_train]: 1-indexed species/site indices.
- x_train_obs[N_train]: continuous environmental covariate observed WITH measurement error.
- y_train[N_train]: non-negative integer counts.
- Analogous test arrays (species_test, site_test, x_test_obs, y_test).
- Note: ~20% of the full species*site grid is missing at random (MAR); you only see the observed rows.

MODEL:
- y[i] ~ neg_binomial_2(mu[i], phi) with mu[i] = exp(alpha + u_species[species[i]] + v_site[site[i]] + beta * true_env[i]).
- u_species[s] ~ Normal(0, sigma_species)   (non-centered parameterization)
- v_site[l] ~ Normal(0, sigma_site)         (non-centered parameterization)
- Classical measurement-error correction: treat the true covariate as latent.
    true_env[i] ~ Normal(0, 1)
    x_obs[i] ~ Normal(true_env[i], sigma_me)
- Parameter names (exact): alpha, beta, u_species, v_site, sigma_species, sigma_site, phi, sigma_me, true_env.
- Weakly informative priors on alpha, beta, sigma_*, phi, sigma_me.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.crossed_re_counts.minimal",
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
    id="stan.crossed_re_counts.detailed",
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

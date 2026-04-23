"""Real-data spatio-temporal outbreak task (Adeoye 2025, arXiv:2503.01456).

Monthly IMD disease case counts for 28 European countries over 84 months, plus
country-level population denominators and a spatial adjacency graph. The task
is to build a spatio-temporal Poisson (or NB) model in Stan and score it by
held-out ELPD on the final 12 months.

Source data: https://github.com/Matthewadeoye/DetectOutbreaks (data/*.rda).
The .rda files are pre-converted to JSON at import time and cached on disk so
subsequent imports are fast; set OUTBREAK_REBUILD=1 to force re-conversion.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

_CACHE_DIR = Path(os.environ.get(
    "OUTBREAK_CACHE_DIR", "/home/godli/eval-work/data-cache/outbreak"
))
_JSON_PATH = _CACHE_DIR / "stan_data.json"
_RDA_DIR = _CACHE_DIR  # expects ApplicationCounts.rda etc. alongside


def _build_from_rda() -> dict:
    """Fallback: convert the three .rda files into the Stan data dict."""
    import numpy as np
    import pyreadr

    counts = np.array(
        np.asarray(pyreadr.read_r(_RDA_DIR / "ApplicationCounts.rda")["ApplicationCounts"]),
        dtype=float,
    ).copy()
    pop = np.array(
        pyreadr.read_r(_RDA_DIR / "ApplicationPopulation.rda")["ApplicationPopulation"],
        dtype=float,
    ).copy()
    adj = np.array(
        pyreadr.read_r(_RDA_DIR / "ApplicationAdjMat.rda")["ApplicationAdjMat"],
        dtype=float,
    ).copy()

    # Missing counts -> 0 (treated as not-reported). Missing population -> row median.
    counts = np.nan_to_num(counts, nan=0.0)
    for i in range(pop.shape[0]):
        row = pop[i].copy()
        med = np.nanmedian(row)
        row[np.isnan(row)] = med
        pop[i] = row

    N, T = counts.shape
    T_holdout = 12
    T_train = T - T_holdout

    node1, node2 = [], []
    for i in range(N):
        for j in range(i + 1, N):
            if adj[i, j] > 0.5:
                node1.append(i + 1)
                node2.append(j + 1)

    return {
        "N": int(N),
        "T_train": int(T_train),
        "T_test": int(T_holdout),
        "y_train": counts[:, :T_train].astype(int).tolist(),
        "y_test": counts[:, T_train:].astype(int).tolist(),
        "pop_train": pop[:, :T_train].tolist(),
        "pop_test": pop[:, T_train:].tolist(),
        "N_edges": len(node1),
        "node1": node1,
        "node2": node2,
    }


def _load_stan_data() -> dict:
    if _JSON_PATH.exists() and not os.environ.get("OUTBREAK_REBUILD"):
        with open(_JSON_PATH) as f:
            return json.load(f)
    data = _build_from_rda()
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_JSON_PATH, "w") as f:
        json.dump(data, f)
    return data


_STAN_DATA = _load_stan_data()
# Stan doesn't allow non-data variables as vector sizes at top level of
# generated quantities, so we pre-compute the flat test-observation count
# as a data field instead of having Claude derive it.
_STAN_DATA["N_test_obs"] = int(_STAN_DATA["N"] * _STAN_DATA["T_test"])
_DATA_JSON = json.dumps(_STAN_DATA)


_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains a TRAINING set (y_train, pop_train of shape N x T_train) and a TEST set (y_test, pop_test of shape N x T_test) covering the next T_test months for the same N countries. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. The data block already includes `int N_test_obs` (= N * T_test, precomputed). In the `generated quantities` block, compute a flat log-likelihood vector over ALL test observations (country i, test-month t), in row-major order (country outer, month inner):

     vector[N_test_obs] log_lik_test;
     {
       int k = 1;
       for (i in 1:N)
         for (t in 1:T_test) {
           log_lik_test[k] = <log density of y_test[i, t] given current parameters, pop_test[i, t], and the appropriate temporal/spatial index>;
           k += 1;
         }
     }

Your model will be scored by the held-out ELPD: sum over test observations of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a spatio-temporal Poisson model in Stan for monthly disease case counts in "
    "28 countries. Data in data.json has countries x months counts (y_train, y_test), "
    "population denominators (pop_train, pop_test; use as log offsets), and a spatial "
    "adjacency graph (edge list: N_edges, node1, node2; 1-indexed, node1 < node2). "
    "Include a smooth temporal component and a spatial random effect."
    + _ELPD_CLAUSE
)

_DETAILED_PROMPT = """Build a spatio-temporal disease-count model in Stan matching this specification.

DATA (in data.json):
- N = 28 countries, T_train months of training data, T_test months of holdout (same countries).
- y_train[N, T_train], y_test[N, T_test]: monthly case counts (non-negative integers).
- pop_train[N, T_train], pop_test[N, T_test]: population denominators. Use log(pop) as an offset.
- Spatial graph: N_edges, node1[N_edges], node2[N_edges] (1-indexed, node1 < node2).

MODEL:
- Observation: y[i, t] ~ NegBinomial (overdispersed Poisson; equivalently Poisson-Gamma). Use neg_binomial_2_log for numerical stability.
- Linear predictor: log_mu[i, t] = log(pop[i, t]) + alpha + nu[t] + phi[i]
- Temporal component nu[t]: RW1 or RW2, nu[t] - nu[t-1] ~ Normal(0, sigma_nu), with nu[1] = 0 (anchor) or equivalent identifiability.
- Spatial component phi[i]: ICAR prior over the adjacency graph, with sum-to-zero constraint sum(phi) = 0 for identifiability. Parameterize via phi_raw (unconstrained) then phi = phi_raw - mean(phi_raw), and the pairwise difference prior:
     target += -0.5 * dot_self(phi_raw[node1] - phi_raw[node2]);
- Overdispersion: y ~ neg_binomial_2_log(log_mu, rho_t), with reciprocal dispersion rho_t > 0. (You may also use a Poisson-Gamma / Poisson-lognormal; pick one and stick with it.)
- Priors: alpha ~ Normal(0, 5); sigma_nu, sigma_phi ~ Normal+(0, 1); rho_t ~ Normal+(0, 5) or Gamma.

REQUIRED PARAMETER NAMES (use these exact names so the model is legible):
  alpha, nu (vector[T_train]), phi_raw (vector[N]), phi (transformed, sum-to-zero),
  sigma_nu, sigma_phi, rho_t (NB reciprocal dispersion), mu (if you expose it).

For test-time prediction, extrapolate nu forward: nu_test[t] ~ Normal(nu_test[t-1], sigma_nu) starting from nu[T_train]. You may integrate this into generated quantities (sample nu_test once per draw).
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.outbreak_real.minimal",
    prompt=_MINIMAL_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
        n_warmup=500,
        n_sampling=500,
        adapt_delta=0.95,
    ),
    timeout_s=1800,
    expected_duration_s=600,
))

register(TaskSpec(
    id="stan.outbreak_real.detailed",
    prompt=_DETAILED_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
        n_warmup=500,
        n_sampling=500,
        adapt_delta=0.95,
    ),
    timeout_s=1800,
    expected_duration_s=600,
))

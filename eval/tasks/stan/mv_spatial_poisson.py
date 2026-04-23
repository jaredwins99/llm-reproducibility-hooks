"""Multivariate spatial Poisson with latent factors, offsets, and MNAR missingness.

D=3 disease outcomes observed across N=36 regions on a 6x6 grid (rook
adjacency). Two spatial latent factors capture residual dependence; zero
counts are missing-not-at-random. Scored by held-out ELPD on a 20% cell split.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    grid=6,  # 6x6 -> N=36
    D=3,
    mu=[0.0, 0.5, -0.3],
    lam=[[1.0, 0.0], [0.7, 0.5], [0.3, 0.8]],
    sigma_F1=1.0,
    sigma_F2=0.8,
    p_miss_zero=0.3,
    test_frac=0.2,
    seed=42,
)


def _rook_edges(g: int):
    """Return list of (a, b) 1-indexed edges with a<b for a g x g rook grid."""
    edges = []
    for r in range(g):
        for c in range(g):
            i = r * g + c + 1
            if c + 1 < g:
                j = r * g + (c + 1) + 1
                edges.append((i, j))
            if r + 1 < g:
                j = (r + 1) * g + c + 1
                edges.append((i, j))
    return edges


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    g = c["grid"]
    N = g * g
    D = c["D"]
    mu = np.array(c["mu"], dtype=float)
    lam = np.array(c["lam"], dtype=float)  # (D, 2)

    edges = _rook_edges(g)
    N_edges = len(edges)
    node1 = [a for a, _ in edges]
    node2 = [b for _, b in edges]

    # Spatial latent factors: simple proxy — iid normal, sum-to-zero centered.
    F1 = rng.normal(0.0, c["sigma_F1"], N)
    F1 = F1 - F1.mean()
    F2 = rng.normal(0.0, c["sigma_F2"], N)
    F2 = F2 - F2.mean()

    E = np.ones(N, dtype=float)

    # Sample y[i, d]
    y = np.zeros((N, D), dtype=int)
    for i in range(N):
        for d in range(D):
            log_rate = mu[d] + lam[d, 0] * F1[i] + lam[d, 1] * F2[i]
            rate = E[i] * np.exp(log_rate)
            y[i, d] = rng.poisson(rate)

    # MNAR: zero counts missing with prob p_miss_zero; positives always observed.
    observed = np.ones((N, D), dtype=bool)
    p_miss = c["p_miss_zero"]
    for i in range(N):
        for d in range(D):
            if y[i, d] == 0 and rng.random() <= p_miss:
                observed[i, d] = False

    # Collect observed cells, then 80/20 train/test split.
    cells = [(i, d) for i in range(N) for d in range(D) if observed[i, d]]
    rng.shuffle(cells)
    n_test = int(round(c["test_frac"] * len(cells)))
    test_cells = cells[:n_test]
    train_cells = cells[n_test:]

    def pack(cs):
        region = [i + 1 for i, _ in cs]
        outcome = [d + 1 for _, d in cs]
        yy = [int(y[i, d]) for i, d in cs]
        return region, outcome, yy

    region_train, outcome_train, y_train = pack(train_cells)
    region_test, outcome_test, y_test = pack(test_cells)

    return {
        "N": N,
        "D": D,
        "N_edges": N_edges,
        "node1": node1,
        "node2": node2,
        "E": E.tolist(),
        "n_obs_train": len(train_cells),
        "region_train": region_train,
        "outcome_train": outcome_train,
        "y_train": y_train,
        "n_obs_test": len(test_cells),
        "region_test": region_test,
        "outcome_test": outcome_test,
        "y_test": y_test,
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (n_obs_train, region_train, outcome_train, y_train) and a TEST set (n_obs_test, region_test, outcome_test, y_test) of the same format. Shared structure: N regions, D outcomes, N_edges edges (node1, node2 both 1-indexed with node1<node2), and offsets E[i]. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[n_obs_test] log_lik_test;
     for (i in 1:n_obs_test)
       log_lik_test[i] = <log density of y_test[i] given current parameters, region_test[i], outcome_test[i], and E[region_test[i]]>;

Your model will be scored by the held-out ELPD: sum over test cells of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a multivariate spatial Poisson model in Stan with latent spatial factors. "
    "The data has D=3 outcomes observed across N regions on a grid adjacency graph, "
    "with offsets E[i] and MNAR missingness. Use latent factors to capture residual "
    "spatial dependence."
) + _ELPD_CLAUSE


_DETAILED_PROMPT = """Build a multivariate spatial Poisson model in Stan with latent spatial factors.

DATA (in data.json):
- N regions on a grid; D = 3 outcomes per region.
- Adjacency graph: N_edges undirected edges, given as node1[1..N_edges], node2[1..N_edges] (1-indexed, node1 < node2).
- Offsets E[1..N] (expected counts).
- Observed training cells: n_obs_train triples (region_train[i], outcome_train[i], y_train[i]). Likewise n_obs_test for held-out cells. MNAR: zero counts are more often missing than positives.

MODEL:
- For each observed cell (i, d): y[i, d] ~ Poisson(E[i] * exp(mu[d] + lambda[d, 1] * F1[i] + lambda[d, 2] * F2[i])).
  Use `poisson_log` with linear predictor log(E[i]) + mu[d] + lambda[d,1]*F1[i] + lambda[d,2]*F2[i].
- Latent spatial factors F1, F2 each vector[N], ICAR via pairwise-difference prior:
      target += -0.5 * dot_self(F1[node1] - F1[node2]);
      target += -0.5 * dot_self(F2[node1] - F2[node2]);
  Add a soft sum-to-zero constraint: sum(F1) ~ normal(0, 0.001 * N); same for F2.
- Scale parameters sigma_F1, sigma_F2 (positive); multiply factors by their scale non-centered where applicable.
- Loading matrix lambda has shape [D, 2]. For identifiability, FIX the first row: lambda[1, 1] = 1, lambda[1, 2] = 0. Other entries are free parameters with weakly informative normal priors.
- mu: vector[D] of global log-rate offsets, weakly informative priors.
- Weakly informative priors on sigma_F1, sigma_F2 (e.g., half-normal).

Parameter names (required): mu, lambda, F1, F2, sigma_F1, sigma_F2.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.mv_spatial_poisson.minimal",
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
    id="stan.mv_spatial_poisson.detailed",
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

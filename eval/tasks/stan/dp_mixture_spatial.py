"""Hierarchical DP mixture with spatial smoothing (truncated stick-breaking).

Observations are grouped into G spatial regions arranged in a 3x4 grid with
rook adjacency. Within each group, y is drawn from a K_true=3 Gaussian
mixture whose weights vary smoothly across neighboring regions. The model
is scored by held-out ELPD under a truncated-stick-breaking DP mixture
(K_max=8) with spatially smoothed group weights.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

DGP_CONFIG = dict(
    N=300,
    grid_rows=3,
    grid_cols=4,
    K_true=3,
    K_max=8,
    mu=[-3.0, 0.0, 3.0],
    sigma=[0.7, 1.0, 0.6],
    w_pop=[0.4, 0.35, 0.25],
    noise_scale=0.1,
    test_frac=0.2,
    seed=42,
)


def _build_adjacency(rows: int, cols: int):
    """Rook adjacency for a rows x cols grid. Returns (G, edges list of (a,b) with a<b, both 1-indexed)."""
    G = rows * cols
    edges = []
    for r in range(rows):
        for c in range(cols):
            g = r * cols + c
            if c + 1 < cols:
                edges.append((g, g + 1))
            if r + 1 < rows:
                edges.append((g, g + cols))
    # 1-index
    edges = [(a + 1, b + 1) for (a, b) in edges]
    return G, edges


def _spatial_smooth(rng, rows: int, cols: int, K: int, passes: int = 2) -> np.ndarray:
    """Return (G, K) noise that's been spatially averaged with neighbors."""
    G = rows * cols
    eps = rng.normal(0.0, 1.0, size=(G, K))
    # Build neighbor list
    nbrs = [[] for _ in range(G)]
    for r in range(rows):
        for c in range(cols):
            g = r * cols + c
            if c + 1 < cols:
                nbrs[g].append(g + 1)
                nbrs[g + 1].append(g)
            if r + 1 < rows:
                nbrs[g].append(g + cols)
                nbrs[g + cols].append(g)
    for _ in range(passes):
        new = eps.copy()
        for g in range(G):
            if nbrs[g]:
                new[g] = 0.5 * eps[g] + 0.5 * np.mean(eps[nbrs[g]], axis=0)
        eps = new
    # Re-center so mean over groups is ~0 per component
    eps = eps - eps.mean(axis=0, keepdims=True)
    return eps


def simulate() -> dict:
    c = DGP_CONFIG
    rng = np.random.RandomState(c["seed"])
    rows, cols = c["grid_rows"], c["grid_cols"]
    G, edges = _build_adjacency(rows, cols)
    K_true = c["K_true"]
    mu = np.array(c["mu"])
    sigma = np.array(c["sigma"])
    w_pop = np.array(c["w_pop"])

    eps = _spatial_smooth(rng, rows, cols, K_true)
    w_g = w_pop[None, :] + c["noise_scale"] * eps
    w_g = np.clip(w_g, 1e-3, None)
    w_g = w_g / w_g.sum(axis=1, keepdims=True)

    N = c["N"]
    # Assign each observation a group uniformly at random
    groups = rng.randint(0, G, size=N)
    zs = np.zeros(N, dtype=int)
    ys = np.zeros(N)
    for i in range(N):
        g = groups[i]
        zs[i] = rng.choice(K_true, p=w_g[g])
        ys[i] = rng.normal(mu[zs[i]], sigma[zs[i]])

    # Train/test split — 20% held out, stratified roughly by random
    idx = np.arange(N)
    rng.shuffle(idx)
    n_test = int(round(c["test_frac"] * N))
    test_idx = np.sort(idx[:n_test])
    train_idx = np.sort(idx[n_test:])

    node1 = [a for (a, _) in edges]
    node2 = [b for (_, b) in edges]

    return {
        "N_train": int(len(train_idx)),
        "N_test": int(len(test_idx)),
        "G": int(G),
        "K_max": int(c["K_max"]),
        "n_edges": int(len(edges)),
        "node1": node1,
        "node2": node2,
        "group_train": (groups[train_idx] + 1).tolist(),
        "y_train": ys[train_idx].tolist(),
        "group_test": (groups[test_idx] + 1).tolist(),
        "y_test": ys[test_idx].tolist(),
    }


_STAN_DATA = simulate()
_DATA_JSON = json.dumps(_STAN_DATA)

_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (N_train, y_train, group_train) and a TEST set (N_test, y_test, group_test), along with spatial adjacency (G, n_edges, node1, node2) and the mixture truncation K_max. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = log( sum_{k=1..K_max} w_group[group_test[i], k] * Normal(y_test[i] | mu[k], sigma[k]) );

   (i.e. the mixture predictive log-density at the test point's group.)

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a hierarchical Dirichlet Process mixture model in Stan with spatial smoothing. "
    "Observations are grouped by spatial region (with an adjacency graph). Within each group, "
    "observations come from a mixture of K_max Gaussian components (with DP prior on weights) "
    "where weights are spatially smoothed across neighboring regions."
) + _ELPD_CLAUSE

_DETAILED_PROMPT = """Build a hierarchical Dirichlet Process mixture model in Stan with spatial smoothing.

DATA (in data.json):
- N_train, N_test observations; y_train, y_test are real-valued.
- G spatial groups on an adjacency graph given by n_edges / node1 / node2 (both 1-indexed).
- group_train[i], group_test[i]: 1-indexed group membership.
- K_max: truncation level of the stick-breaking DP (K_max = 8).

MODEL:
- Truncated stick-breaking at K_max:
    v_breaks[k] ~ Beta(1, alpha_dp)  for k = 1..K_max-1
    w_pop[k] = v_breaks[k] * prod_{j<k} (1 - v_breaks[j]),  w_pop[K_max] = prod_{j<K_max}(1 - v_breaks[j])
- Concentration hyperprior: alpha_dp ~ Gamma(2, 2) (or similar weakly informative).
- Group-level weights w_group[g, 1..K_max]: spatially smoothed around w_pop. Either
    (a) w_group[g] ~ Dirichlet(kappa * w_pop) with a CAR / ICAR-like smoothing prior on
        logit(w_group) across edges (node1, node2), or
    (b) hierarchical w_group[g] ~ Dirichlet(alpha_g * w_pop) with a CAR prior on log(alpha_g).
  Either parameterization is acceptable as long as w_group[g] is a simplex and
  neighbors (node1[e], node2[e]) are coupled.
- Component parameters: mu[k] ~ Normal(0, 5) (ordered to break label-switching is encouraged),
  sigma[k] ~ Half-Normal(0, 2) or similar.
- Likelihood: y_train[i] ~ sum_{k} w_group[group_train[i], k] * Normal(mu[k], sigma[k]).

Name parameters exactly: alpha_dp, v_breaks, w_pop, w_group, mu, sigma.
""" + _ELPD_CLAUSE


register(TaskSpec(
    id="stan.dp_mixture_spatial.minimal",
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
    id="stan.dp_mixture_spatial.detailed",
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

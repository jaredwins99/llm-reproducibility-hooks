"""Besag York Mollié (BYM) spatial Poisson task.

Ground-truth DGP:
  For region i on a 6x6 grid with rook adjacency:
    y[i] ~ Poisson(E[i] * exp(mu + theta[i] + phi[i]))
    theta[i] ~ Normal(0, sigma_theta)        — unstructured heterogeneity
    phi      ~ ICAR(0, sigma_phi)            — structured spatial
    E[i] = 1.0

Fixed DGP config below is load-bearing: changing any value invalidates prior runs.
Data is generated once at import time (seed=42), so all trials of this task see
the same data and the same ground truth.
"""
from __future__ import annotations

import json

import numpy as np

from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer
from eval.tasks import register

DGP_CONFIG = dict(
    rows=6, cols=6,
    mu=0.0,
    sigma_theta=0.3,
    sigma_phi=0.5,
    seed=42,
)


def _rook_edges(rows: int, cols: int) -> list[tuple[int, int]]:
    """Return 1-indexed (node1, node2) edges with node1 < node2 for a rook-adjacency grid."""
    edges: list[tuple[int, int]] = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if c + 1 < cols:
                j = r * cols + (c + 1)
                edges.append((i + 1, j + 1))
            if r + 1 < rows:
                j = (r + 1) * cols + c
                edges.append((i + 1, j + 1))
    return edges


def simulate() -> tuple[dict, dict, np.ndarray]:
    """Return (stan_data, true_params, y_obs). Deterministic under config seed."""
    c = DGP_CONFIG
    rows, cols = c["rows"], c["cols"]
    N = rows * cols

    rng = np.random.RandomState(c["seed"])

    edges = _rook_edges(rows, cols)
    node1 = [e[0] for e in edges]
    node2 = [e[1] for e in edges]
    N_edges = len(edges)

    theta = rng.normal(0.0, c["sigma_theta"], N)
    phi_raw = rng.normal(0.0, c["sigma_phi"], N)
    phi = phi_raw - phi_raw.mean()

    eta = c["mu"] + theta + phi
    y = rng.poisson(np.exp(eta))

    E = [1.0] * N

    stan_data = {
        "N": N,
        "N_edges": N_edges,
        "node1": node1,
        "node2": node2,
        "y": y.astype(int).tolist(),
        "E": E,
    }
    true_params = {
        "mu": c["mu"],
        "sigma_theta": c["sigma_theta"],
        "sigma_phi": c["sigma_phi"],
    }
    return stan_data, true_params, y


_STAN_DATA, _TRUE_PARAMS, _Y_OBS = simulate()

# Canonical semantic roles for the scored population-level parameters. Keys are
# the role names; values are one-line descriptions fed to the judge when it has
# to infer the role -> Stan name mapping from model.stan.
CANONICAL_ROLES = {
    "intercept_mu": "global intercept (log-rate baseline)",
    "sd_unstruct":  "sd of unstructured random effect (theta / heterogeneity)",
    "sd_struct":    "sd of structured spatial effect (phi / CAR)",
}

# True values keyed by canonical role.
ROLE_TRUE_VALUES: dict[str, float | list[float]] = {
    "intercept_mu": _TRUE_PARAMS["mu"],
    "sd_unstruct":  _TRUE_PARAMS["sigma_theta"],
    "sd_struct":    _TRUE_PARAMS["sigma_phi"],
}

# Static candidate names used as a last resort if params.json is missing AND
# judge inference fails. Preserves graceful degradation.
FALLBACK_MAP = {
    "intercept_mu": ["mu", "beta0", "alpha", "intercept", "beta_0"],
    "sd_unstruct":  ["sigma_theta", "tau_theta", "sigma_unstruct", "sd_theta"],
    "sd_struct":    ["sigma_phi", "tau_phi", "sigma_car", "sd_phi", "sigma_spatial"],
}


def _build_scorer() -> StanScorer:
    return StanScorer(
        data=_STAN_DATA,
        true_params=ROLE_TRUE_VALUES,
        canonical_roles=CANONICAL_ROLES,
        fallback_map=FALLBACK_MAP,
        observed_y=_Y_OBS,
        is_zero_inflated=False,
        has_spatial=True,
        expected_artifacts=["simulate_data.py", "params.json"],
        n_warmup=500,
        n_sampling=500,
    )


_DATA_JSON = json.dumps(_STAN_DATA)


_PARAMS_JSON_INSTRUCTION = """

Also produce a params.json file in the current directory mapping these canonical roles to the Stan parameter names you used in your model. Only include roles that exist in your parameterization; omit any that don't apply.

Roles:
- "intercept_mu": global intercept (log-rate baseline)
- "sd_unstruct":  sd of unstructured random effect (theta / heterogeneity)
- "sd_struct":    sd of structured spatial effect (phi / CAR)

Format: a single JSON object. Example:
{"intercept_mu": "mu", "sd_unstruct": "sigma_theta", "sd_struct": "sigma_phi"}"""


_MINIMAL_PROMPT = """Build a Besag York Mollié (BYM) spatial Poisson regression model in Stan for disease mapping. Data in data.json has N regions, N_edges, node1[N_edges] and node2[N_edges] (1-indexed edge endpoints for adjacency), y[N] counts, E[N] expected counts. Include both unstructured heterogeneity and a structured spatial (ICAR) component. Save model.stan. Include generated quantities y_rep.""" + _PARAMS_JSON_INSTRUCTION


_DETAILED_PROMPT = """Build a Besag York Mollié (BYM) spatial Poisson regression model in Stan for disease mapping with the following specification.

DATA (in data.json):
- N regions
- N_edges: number of undirected edges in the adjacency graph
- node1[N_edges], node2[N_edges]: 1-indexed edge endpoints (node1 < node2)
- y[N]: non-negative integer observed counts
- E[N]: expected counts (offsets)

MODEL:
- y[i] ~ Poisson(E[i] * exp(mu + theta[i] + phi[i]))
- theta[i] ~ Normal(0, sigma_theta)  — unstructured heterogeneity (use non-centered parameterization)
- phi: intrinsic CAR (ICAR) component, implemented via the pairwise difference formulation:
    target += -0.5 * dot_self(phi[node1] - phi[node2]);
  with a soft sum-to-zero constraint on phi (e.g. sum(phi) ~ normal(0, 0.001 * N)).

PRIORS:
- mu ~ normal(0, 5)
- sigma_theta ~ normal(0, 1)   (half-normal via <lower=0>)
- sigma_phi   ~ normal(0, 1)   (half-normal via <lower=0>)

EXACT PARAMETER NAMES (use these exactly): mu, theta, phi, sigma_theta, sigma_phi.

OUTPUT:
- Save the model to model.stan.
- Include a generated quantities block producing y_rep for posterior predictive checks.""" + _PARAMS_JSON_INSTRUCTION


_COMMON = dict(
    initial_files={"data.json": _DATA_JSON},
    scorer=_build_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
)

register(TaskSpec(id="stan.spatial_car.minimal", prompt=_MINIMAL_PROMPT, **_COMMON))
register(TaskSpec(id="stan.spatial_car.detailed", prompt=_DETAILED_PROMPT, **_COMMON))

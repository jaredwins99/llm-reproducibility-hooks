"""Real-data task: hierarchical Bayesian logistic regression on HiBayES eval logs.

Data from HiBayES 2025 (arXiv:2505.05602). Per-item binary correctness for
GPT-4o and Claude-Sonnet-3.5 on three Inspect-format benchmarks (boolq, mbpp,
race-h). Extracted from the .eval zip logs in the hibayes repo:
  examples/hibayes-usecases/data/{gpt-4o,claude-sonnet-3-5}/*.eval
The extractor (data-cache/hibayes/extract.py) caches the Stan-ready dict to
stan_data.json. This module loads that cache at import — it does NOT re-parse.

Task: held-out ELPD on 20% random split of (model, task, item) rows.
"""
from __future__ import annotations

import json
from pathlib import Path

from eval.harness.spec import TaskSpec
from eval.scoring.elpd import ELPDScorer
from eval.tasks import register

_CACHE = Path("/home/godli/eval-work/data-cache/hibayes/stan_data.json")
if not _CACHE.exists():
    raise FileNotFoundError(
        f"Missing cached Stan data at {_CACHE}. "
        "Run /home/godli/eval-work/data-cache/hibayes/extract.py first."
    )

_RAW = json.loads(_CACHE.read_text())
# Strip metadata fields (leading underscore) before passing to Stan.
_RAW_DATA = {k: v for k, v in _RAW.items() if not k.startswith("_")}
# Normalize key naming: N_<X> for all scalar counts (consistent with other
# tasks in the bank). Rename n_train/n_test to N_train/N_test so Claude
# can't confuse "n_ for counts" vs "N_ for groups" conventions.
_RENAME = {"n_train": "N_train", "n_test": "N_test"}
_STAN_DATA = {_RENAME.get(k, k): v for k, v in _RAW_DATA.items()}
_DATA_JSON = json.dumps(_STAN_DATA)


_ELPD_CLAUSE = """

PREDICTIVE HOLDOUT: data.json contains both a TRAINING set (N_train, model_train, task_train, item_train, y_train) and a TEST set (N_test, model_test, task_test, item_test, y_test). All index arrays are 1-indexed. Your Stan model MUST:

1. Fit using ONLY the training data — the likelihood should use y_train, not y_test.
2. In the `generated quantities` block, compute:

     vector[N_test] log_lik_test;
     for (i in 1:N_test)
       log_lik_test[i] = bernoulli_logit_lpmf(y_test[i] | <linear predictor for test row i>);

Your model will be scored by the held-out ELPD: sum over test points of log mean posterior predictive density. Higher ELPD = better prediction.

Save your Stan model to model.stan in the current directory."""


_MINIMAL_PROMPT = (
    "Build a hierarchical Bayesian logistic regression model in Stan for binary "
    "AI-evaluation outcomes. Include random effects for model, task, and item.\n\n"
    "Your data block should match the fields in data.json EXACTLY (case-sensitive):\n"
    "- `int<lower=1> N_models;`   number of unique models\n"
    "- `int<lower=1> N_tasks;`    number of unique tasks\n"
    "- `int<lower=1> N_items;`    number of unique items\n"
    "- `int<lower=1> N_train;`    number of training rows\n"
    "- `int<lower=1> N_test;`     number of test rows\n"
    "- Integer index arrays (1-indexed): model_train/test, task_train/test, item_train/test\n"
    "- Binary outcomes: y_train, y_test (ints 0 or 1)"
) + _ELPD_CLAUSE


_DETAILED_PROMPT = """Build a hierarchical Bayesian logistic regression model in Stan for binary AI-evaluation outcomes.

DATA (in data.json, use these exact names in your Stan data block):
- N_models, N_tasks, N_items: counts of unique models, tasks, and items (items are globally indexed; each item belongs to exactly one task).
- N_train training rows, N_test test rows.
- For each training row i: model_train[i] in 1..N_models, task_train[i] in 1..N_tasks, item_train[i] in 1..N_items, y_train[i] in {0, 1}.
- Parallel arrays model_test, task_test, item_test, y_test of length N_test.

MODEL:
- y[i] ~ Bernoulli_logit(mu + alpha_model[model[i]] + beta_task[task[i]] + gamma_item[item[i]])
  where:
    * mu is a global intercept (overall log-odds of correctness).
    * alpha_model[m] ~ Normal(0, sigma_model) captures per-model ability.
    * beta_task[t] ~ Normal(0, sigma_task) captures per-task difficulty.
    * gamma_item[j] ~ Normal(0, sigma_item) captures per-item difficulty (nested within task — each item already belongs to one task, so a flat item effect suffices).
- Use non-centered parameterization for alpha_model, beta_task, and gamma_item.
- Weakly informative priors: mu ~ Normal(0, 2); sigma_model, sigma_task, sigma_item ~ Normal+(0, 1) or half-Normal(0, 1).

REQUIRED PARAMETER NAMES (exact): mu, alpha_model, beta_task, gamma_item, sigma_model, sigma_task, sigma_item.
""" + _ELPD_CLAUSE


def _scorer() -> ELPDScorer:
    return ELPDScorer(
        data=_STAN_DATA,
        expected_artifacts=["model.stan"],
        run_judge=False,
        n_warmup=500,
        n_sampling=500,
    )


register(TaskSpec(
    id="stan.aieval_real.minimal",
    prompt=_MINIMAL_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
))

register(TaskSpec(
    id="stan.aieval_real.detailed",
    prompt=_DETAILED_PROMPT,
    initial_files={"data.json": _DATA_JSON},
    scorer=_scorer(),
    timeout_s=1800,
    expected_duration_s=600,
))

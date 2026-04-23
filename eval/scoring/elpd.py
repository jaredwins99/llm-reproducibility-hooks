"""ELPDScorer — score a Stan trial by held-out predictive log-density.

Parameterization-invariant: doesn't care what Claude named parameters or which
model class they chose. Asks only "how well does your fitted model predict the
held-out test set?"

Protocol:
  - Task provides stan_data with BOTH training and test sections, e.g.:
      { N_train, y_train, x_train, N_test, y_test, x_test, ... }
  - Claude's model likelihood uses ONLY the training data.
  - Claude's generated quantities block computes:
      vector[N_test] log_lik_test;
    with log_lik_test[i] = log p(y_test[i] | x_test[i], draw)
  - Scorer extracts log_lik_test draws (shape: n_draws x N_test), computes:
      elpd_point[i] = log mean_s exp(log_lik_test[s, i])  (logsumexp - log S)
      elpd_total    = sum_i elpd_point[i]
      elpd_se       = sqrt(N_test * var(elpd_point))

ELPD is monotonic in predictive quality: higher = better. Zero is the reference
of an uninformative predictive distribution.

Also reports engineering metrics: compiles, fits, divergences, max_rhat,
min_ess, compile_s, fit_s. Plus optional judge rubric.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import logsumexp


@dataclass
class ELPDScorer:
    """Score a trial by held-out log predictive density on test observations.

    Attributes:
        data: stan_data with train + test sections. Must include N_train, N_test,
            and log_lik_test-relevant fields (y_test, x_test, etc.).
        expected_artifacts: files Claude was expected to produce (e.g., params.json).
        n_chains, n_warmup, n_sampling, adapt_delta, random_seed: sampler config.
        run_judge: if True, spawn a judge subagent to score interpretability.
        judge_rubric: if given, a list of (criterion_name, description) tuples
            fed to the judge. Scores are 0-5 per criterion.
        judge_model: model for the judge call.
    """

    data: dict
    expected_artifacts: list[str] = field(default_factory=list)
    n_chains: int = 4
    n_warmup: int = 500
    n_sampling: int = 500
    adapt_delta: float = 0.95
    random_seed: int = 42
    run_judge: bool = False
    judge_rubric: list[tuple[str, str]] = field(default_factory=list)
    judge_model: str = "haiku"

    def __call__(self, trial_dir: Path) -> dict[str, Any]:
        result: dict[str, Any] = {
            "compiles": False,
            "fits": False,
            "artifacts": self._check_artifacts(trial_dir),
        }

        model_path = trial_dir / "model.stan"
        if not model_path.exists():
            result["error"] = "no model.stan in trial dir"
            return result

        from cmdstanpy import CmdStanModel

        t0 = time.monotonic()
        try:
            model = CmdStanModel(stan_file=str(model_path))
        except Exception as e:
            result["error"] = f"compile failed: {type(e).__name__}: {e}"
            return result
        result["compile_s"] = round(time.monotonic() - t0, 2)
        result["compiles"] = True

        t0 = time.monotonic()
        try:
            fit = model.sample(
                data=self.data,
                chains=self.n_chains,
                iter_warmup=self.n_warmup,
                iter_sampling=self.n_sampling,
                adapt_delta=self.adapt_delta,
                seed=self.random_seed,
                show_progress=False,
                show_console=False,
            )
        except Exception as e:
            result["error"] = f"fit failed: {type(e).__name__}: {e}"
            return result
        result["fit_s"] = round(time.monotonic() - t0, 2)
        result["fits"] = True

        result.update(self._score_diagnostics(fit))
        result.update(self._score_elpd(fit))

        if self.run_judge and self.judge_rubric:
            result["judge"] = self._run_judge(model_path)

        return result

    # ----- sub-scorers -----

    def _check_artifacts(self, trial_dir: Path) -> dict[str, dict[str, Any]]:
        out = {}
        for rel in self.expected_artifacts:
            p = trial_dir / rel
            out[rel] = {"exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0}
        return out

    def _score_diagnostics(self, fit) -> dict[str, Any]:
        summary = fit.summary()
        rhat_col = next((c for c in summary.columns if c.lower() in {"r_hat", "rhat"}), None)
        ess_col = next((c for c in summary.columns if "ess" in c.lower() and "bulk" in c.lower()), None)
        if ess_col is None:
            ess_col = next((c for c in summary.columns if c.lower().startswith("n_eff") or c.lower() == "ess"), None)

        rhat = summary[rhat_col].dropna() if rhat_col else None
        ess = summary[ess_col].dropna() if ess_col else None
        divs = int(sum(fit.divergences)) if hasattr(fit, "divergences") else None

        return {
            "divergences": divs,
            "max_rhat": float(rhat.max()) if rhat is not None and len(rhat) else None,
            "min_ess": float(ess.min()) if ess is not None and len(ess) else None,
        }

    def _score_elpd(self, fit) -> dict[str, Any]:
        """Compute ELPD from log_lik_test draws if present."""
        try:
            log_lik = fit.stan_variable("log_lik_test")
        except Exception:
            return {"elpd_total": None, "elpd_se": None, "elpd_error": "no log_lik_test in generated quantities"}

        log_lik = np.asarray(log_lik)
        if log_lik.ndim != 2:
            return {"elpd_total": None, "elpd_error": f"log_lik_test ndim={log_lik.ndim}, expected 2"}

        # log_lik shape: (n_draws, N_test)
        S, N_test = log_lik.shape
        if S < 4 or N_test < 1:
            return {"elpd_total": None, "elpd_error": f"degenerate log_lik shape {(S, N_test)}"}

        # Filter out NaN / Inf rows (diverged draws)
        finite_mask = np.isfinite(log_lik).all(axis=1)
        n_finite = finite_mask.sum()
        if n_finite < 4:
            return {
                "elpd_total": None,
                "elpd_error": f"only {n_finite}/{S} draws had finite log_lik_test",
            }

        ll_clean = log_lik[finite_mask]
        # elpd_pointwise[i] = log ( (1/S) sum_s exp(ll[s, i]) ) = logsumexp(ll[:, i]) - log S
        elpd_pointwise = logsumexp(ll_clean, axis=0) - np.log(ll_clean.shape[0])
        elpd_total = float(elpd_pointwise.sum())
        elpd_mean = float(elpd_pointwise.mean())
        elpd_se = float(np.sqrt(len(elpd_pointwise) * elpd_pointwise.var(ddof=1)))

        return {
            "elpd_total": elpd_total,
            "elpd_mean_per_point": elpd_mean,
            "elpd_se": elpd_se,
            "n_test": int(N_test),
            "n_draws_used": int(ll_clean.shape[0]),
            "n_draws_total": int(S),
        }

    def _run_judge(self, model_path: Path) -> dict[str, Any]:
        """Spawn `claude -p` to score interpretability against the rubric."""
        rubric_desc = "\n".join(f'- "{name}": {desc} (0-5)' for name, desc in self.judge_rubric)
        prompt = (
            "Read the Stan model at model.stan in the current directory and score it "
            "against the rubric below. Each criterion is 0 (totally absent) to 5 "
            "(exemplary). Return only JSON.\n\n"
            f"Rubric:\n{rubric_desc}\n\n"
            'Output format: {"scores": {criterion: int, ...}, "justifications": {criterion: "brief evidence", ...}}'
        )
        try:
            result = subprocess.run(
                ["claude", "-p", prompt, "--model", self.judge_model, "--dangerously-skip-permissions"],
                cwd=str(model_path.parent),
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
        if result.returncode != 0:
            return {"error": f"judge exit {result.returncode}"}
        m = re.search(r"\{.*\}", result.stdout, re.DOTALL)
        if not m:
            return {"error": "no JSON in judge output"}
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            return {"error": "invalid JSON from judge"}


# Standard rubric for Stan interpretability — reusable across tasks.
DEFAULT_JUDGE_RUBRIC = [
    ("non_centered", "Uses non-centered parameterization where the model is hierarchical"),
    ("priors", "Uses weakly informative priors (not uniform, not absurdly wide)"),
    ("idiomatic", "Uses Stan idioms: poisson_log/bernoulli_logit, multi_normal_cholesky for large N, log_sum_exp for mixtures"),
    ("identifiability", "Enforces identifiability constraints where needed (ordered, simplex, sum-to-zero)"),
    ("clarity", "Readable: sensible parameter names, block structure, minimal commented-out code"),
]

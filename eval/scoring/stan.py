"""StanScorer — scores a Stan trial by compiling, fitting, and checking outputs.

The scorer re-fits Claude's `model.stan` on fixed task data, then reports:

  Diagnostics:  compiles, fits, divergences, max_rhat, min_ess
  Recovery:     coverage_90, rmse, mean_abs_bias, mean_ci_width, interval_score
  PPC:          mean_diff, zero_frac_diff (opt), max_diff (opt), spatial_corr (opt)
  Artifacts:    per-expected-file {exists, size_bytes}
  Timing:       compile_s, fit_s

Parameter names: true_params is keyed by canonical roles (e.g., "obs_lag"). At
scoring time the scorer resolves each role to a Stan parameter name via:
  1. PRIMARY: a `claude -p --model haiku` judge that reads model.stan and
     produces the role -> Stan-name mapping. It is given params.json (if
     Claude wrote one) and fallback_map as hints but decides independently.
  2. If judge fails (timeout/parse error/disabled), params.json is used.
  3. If that's absent too, fallback_map provides static candidate names.

The scorer does NOT read the reference library (per eval-integrity.md).
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


@dataclass
class StanScorer:
    """Score a completed trial by compiling and fitting its model.stan.

    Attributes:
        data: dict passed to the Stan model's data block. Fixed across trials.
        true_params: ground-truth values keyed by CANONICAL ROLE names
            (e.g., "obs_lag"), not Stan names. Roles are resolved to Stan names
            at scoring time via params.json / judge / fallback_map.
        canonical_roles: role -> one-line description, used in the judge prompt
            when params.json is missing.
        observed_y: observations used for PPC comparisons. Shape (N,) or (G, T).
        expected_artifacts: relative paths the task expected Claude to produce.
        fallback_map: optional static candidate-name lists per role, used ONLY
            if both params.json and judge inference fail.
        judge_model: model used for the judge fallback `claude -p` call.
        enable_judge_fallback: if False, skip step 2 and go straight to fallback_map.
        is_zero_inflated: enable zero-fraction PPC.
        has_spatial: enable spatial-correlation PPC (expects y_rep per location).
        n_chains, n_warmup, n_sampling, adapt_delta: sampler config.
        random_seed: passed to Stan for reproducibility of fits.
    """

    data: dict
    true_params: dict[str, float | list[float]]
    canonical_roles: dict[str, str]
    observed_y: np.ndarray
    expected_artifacts: list[str] = field(default_factory=list)
    fallback_map: dict[str, list[str]] = field(default_factory=dict)
    judge_model: str = "haiku"
    enable_judge_fallback: bool = True
    is_zero_inflated: bool = False
    has_spatial: bool = False
    n_chains: int = 4
    n_warmup: int = 500
    n_sampling: int = 500
    adapt_delta: float = 0.95
    random_seed: int = 42

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

        # Resolve canonical roles -> Stan parameter names before recovery scoring.
        role_map, role_source = self._resolve_role_map(trial_dir, model_path)
        result["recovery_role_source"] = role_source
        result["recovery_role_map"] = role_map

        result.update(self._score_diagnostics(fit))
        result.update(self._score_recovery(fit, role_map))
        result.update(self._score_ppc(fit))
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

    def _score_recovery(self, fit, role_map: dict[str, str]) -> dict[str, Any]:
        """Score parameter recovery using the resolved role -> Stan name map.

        For each canonical role in self.true_params, look up role_map[role] to get
        the Stan parameter name. Also try fallback_map[role] candidates if the
        resolved name isn't in the summary.
        """
        summary = fit.summary()
        coverages, biases, sq_errors, widths, interval_scores = [], [], [], [], []
        alpha = 0.1  # 90% interval
        missing: list[str] = []
        matched: dict[str, str] = {}

        for role, index, true_val in self._iter_true_params():
            candidates: list[str] = []
            if role in role_map and role_map[role]:
                candidates.append(role_map[role])
            candidates.extend(self.fallback_map.get(role, []))

            stan_name = self._first_match(candidates, index, summary)
            truth_label = f"{role}[{index}]" if index is not None else role
            if stan_name is None:
                missing.append(truth_label)
                continue
            matched[truth_label] = stan_name

            row = summary.loc[stan_name]
            lo, hi = float(row["5%"]), float(row["95%"])
            mean = float(row["Mean"])

            width = hi - lo
            covered = lo <= true_val <= hi
            miss_left = max(0.0, lo - true_val)
            miss_right = max(0.0, true_val - hi)
            is_val = width + (2.0 / alpha) * (miss_left + miss_right)

            coverages.append(1 if covered else 0)
            biases.append(abs(mean - true_val))
            sq_errors.append((mean - true_val) ** 2)
            widths.append(width)
            interval_scores.append(is_val)

        n = len(coverages)
        return {
            "recovery_n_params": n,
            "recovery_missing_params": missing,
            "recovery_matched_params": matched,
            "coverage_90": float(np.mean(coverages)) if n else None,
            "mean_abs_bias": float(np.mean(biases)) if n else None,
            "rmse": float(np.sqrt(np.mean(sq_errors))) if n else None,
            "mean_ci_width": float(np.mean(widths)) if n else None,
            "mean_interval_score": float(np.mean(interval_scores)) if n else None,
        }

    def _first_match(self, candidates: list[str], index: int | None, summary) -> str | None:
        """Return the first candidate name that exists in the summary index."""
        for c in candidates:
            if not c:
                continue
            stan_name = c if index is None else f"{c}[{index}]"
            if stan_name in summary.index:
                return stan_name
        return None

    def _resolve_role_map(self, trial_dir: Path, model_path: Path) -> tuple[dict[str, str], str]:
        """Resolve canonical roles to Stan parameter names.

        Order: judge (primary) → params.json → fallback_map.
        Returns (map, source). params.json and fallback_map are passed to the
        judge as hints; it may accept, correct, or ignore them.
        """
        params_hint = self._load_params_json(trial_dir)

        if self.enable_judge_fallback:
            judge_map = self._infer_role_map_via_judge(model_path, params_hint)
            if judge_map is not None:
                return judge_map, "judge"

        if params_hint:
            return params_hint, "params.json"
        return {}, "fallback"

    def _load_params_json(self, trial_dir: Path) -> dict[str, str] | None:
        """Read trial_dir/params.json if valid; returns None on absence or parse error."""
        path = trial_dir / "params.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return {k: str(v) for k, v in data.items() if v}

    def _infer_role_map_via_judge(
        self, model_path: Path, params_hint: dict[str, str] | None
    ) -> dict[str, str] | None:
        """Spawn `claude -p` to read model.stan and return role -> Stan name.

        params_hint (from params.json if Claude wrote one) and self.fallback_map
        are passed as hints. The judge is told these are unverified candidates
        and that the Stan code itself is authoritative.
        """
        roles_desc = "\n".join(f'- "{role}": {desc}' for role, desc in self.canonical_roles.items())

        hint_lines = []
        if params_hint:
            hint_lines.append("Author-declared mapping (may be wrong — verify against the code):")
            hint_lines.append(json.dumps(params_hint, indent=2))
        if self.fallback_map:
            hint_lines.append("Common candidate names per role (not authoritative):")
            hint_lines.append(json.dumps(self.fallback_map, indent=2))
        hints_block = ("\n\n" + "\n".join(hint_lines)) if hint_lines else ""

        prompt = (
            "You are auditing a Stan model. Read model.stan in the current directory "
            "and produce a JSON object mapping each canonical role below to the Stan "
            "parameter NAME as written in the model's `parameters` or `transformed "
            "parameters` block. Base your mapping on what the code actually does, NOT "
            "on author-declared hints. Omit a role if no matching parameter exists in "
            "this parameterization.\n\n"
            f"Canonical roles:\n{roles_desc}"
            f"{hints_block}\n\n"
            'Output JSON only, no prose. Example: {"intercept_pop": "mu_alpha", "obs_lag": "mu_beta"}'
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
        except Exception:
            return None
        if result.returncode != 0:
            return None
        match = re.search(r"\{[^{}]*\}", result.stdout, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return {k: str(v) for k, v in data.items() if v}

    def _score_ppc(self, fit) -> dict[str, Any]:
        # Look for y_rep in generated quantities. If absent, skip PPC.
        try:
            y_rep = fit.stan_variable("y_rep")
        except Exception:
            return {"ppc": "no_y_rep"}

        y_obs = np.asarray(self.observed_y)

        obs_mean = float(y_obs.mean())
        rep_means = y_rep.mean(axis=tuple(range(1, y_rep.ndim)))
        pred_mean = float(rep_means.mean())

        result = {
            "ppc_obs_mean": obs_mean,
            "ppc_pred_mean": pred_mean,
            "ppc_mean_diff": abs(obs_mean - pred_mean),
        }

        if self.is_zero_inflated:
            obs_zero_frac = float(np.mean(y_obs == 0))
            rep_zero_fracs = np.mean(y_rep == 0, axis=tuple(range(1, y_rep.ndim)))
            result["ppc_zero_frac_obs"] = obs_zero_frac
            result["ppc_zero_frac_pred"] = float(rep_zero_fracs.mean())
            result["ppc_zero_frac_diff"] = abs(obs_zero_frac - result["ppc_zero_frac_pred"])

        obs_max = float(y_obs.max())
        rep_maxes = y_rep.max(axis=tuple(range(1, y_rep.ndim)))
        result["ppc_max_obs"] = obs_max
        result["ppc_max_pred"] = float(rep_maxes.mean())
        result["ppc_max_diff"] = abs(obs_max - result["ppc_max_pred"])

        if self.has_spatial and y_rep.ndim >= 2:
            per_loc_pred = y_rep.mean(axis=0).flatten()
            per_loc_obs = y_obs.flatten()
            if per_loc_obs.shape == per_loc_pred.shape:
                corr = float(np.corrcoef(per_loc_obs, per_loc_pred)[0, 1])
                result["ppc_spatial_corr"] = corr

        return result

    def _iter_true_params(self):
        """Yield (base_name, index_or_None, true_value) tuples.

        Vector-valued true params expand to one tuple per element with 1-based index.
        Scalar params yield (name, None, value).
        """
        for name, val in self.true_params.items():
            if isinstance(val, (list, tuple, np.ndarray)):
                for i, v in enumerate(val):
                    yield (name, i + 1, float(v))
            else:
                yield (name, None, float(val))

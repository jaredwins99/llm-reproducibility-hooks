# Eval Harness — Architecture

Measures whether forcing Claude to consult ground-truth references (the Stan library in `reference/stan/`) improves code quality on statistical modeling tasks.

Unit of measurement: the **system** (reference library + protocol + rule + hook + search tooling), not "having references" in isolation.

## Directory layout

```
eval/
├── harness/         # Runner code (this directory)
│   ├── ARCHITECTURE.md     # this file
│   ├── run.py              # CLI entrypoint
│   ├── runner.py           # trial execution
│   ├── materialize.py      # builds trial working directories
│   ├── spec.py             # TaskSpec, TrialResult dataclasses
│   └── tests/              # unit tests for materialize + scorer
├── tasks/           # Task registry
│   ├── __init__.py         # registers all tasks
│   └── stan/               # Stan tasks, one module each
│       ├── ingarch.py
│       └── gp_mixture.py
├── scoring/         # Scorers
│   └── stan.py             # StanScorer class
├── results/         # JSONL output per run (gitignored)
│   └── <run_id>.jsonl
└── stan/            # legacy test artifacts (gitignored)
```

## Trial lifecycle

```
for spec in tasks:
    for model in models:
        for variant in variants:          # with-refs, without-refs
            for trial_n in range(N):
                result = run_trial(spec, model, variant, trial_n)
                append_jsonl(results_path, result)
```

Each call to `run_trial`:

1. **Materialize** a fresh trial directory under `<work_dir>/trial-<uuid>/`. Default `work_dir = /tmp/eval-<run_id>/`. Configurable via `--work-dir`.
2. **Invoke** `claude -p "<prompt>" --model <m>` as a subprocess. `cwd = trial_dir`. Captures stdout, stderr, exit code, wall-clock via `time.monotonic()`.
3. **Score** the trial using `spec.scorer.score(trial_dir)`. Returns a dict of metrics.
4. **Record** a single JSONL line to `eval/results/<run_id>.jsonl` with full metadata + metrics.
5. **Cleanup** the trial directory (unless `--keep-dirs` flag is set for debugging).

## Variant materialization

**Without-refs**: fresh task directory containing only the task files. No `.claude/`, no `CLAUDE.md`, no reference library. Claude Code runs with global defaults only. WebFetch and WebSearch remain allowed (that's the baseline).

**With-refs**: same task files, plus:
- `reference/stan/` hard-linked from the shared pool at the repo root. `cp -al` preserves directory structure, uses no extra disk, is not a symlink.
- `.claude/rules/stan.md` copied from `template/modules/_always/files/.claude/rules/stan.md`.
- `.claude/settings.json` with the `.stan`-triggered PreToolUse hook from `template/modules/_always/files/.claude/settings.json.tmpl` (rendered to substitute the correct reference path).
- Permissions allowlist extended to include `Bash(bash reference/stan/search.sh *)`.

Both variants run **outside `dev_template/`** (under `/tmp/` by default) so no parent `CLAUDE.md` leaks in.

## TaskSpec schema

```python
@dataclass(frozen=True)
class TaskSpec:
    id: str                          # unique, e.g. "stan.ingarch"
    prompt: str                      # the task prompt text — byte-identical across variants
    initial_files: dict[str, str]    # filename -> content, created in trial dir before Claude runs
    scorer: Scorer                   # callable that produces metrics
    timeout_s: int                   # hard wall-clock cap for the subprocess
    expected_duration_s: int         # for budget estimates
```

Tasks live in `eval/tasks/stan/<name>.py` and register themselves in `eval/tasks/__init__.py`:

```python
# eval/tasks/stan/ingarch.py
from eval.harness.spec import TaskSpec
from eval.scoring.stan import StanScorer

TASK = TaskSpec(
    id="stan.ingarch",
    prompt="Build a multilevel zero-inflated INGARCH model...",
    initial_files={},
    scorer=StanScorer(expected_params=["mu", "theta", ...]),
    timeout_s=1800,
    expected_duration_s=600,
)
```

## TrialResult / JSONL schema

One JSON object per line. Fields:

```json
{
  "run_id": "20260421-151212",
  "trial_id": "uuid",
  "timestamp": "2026-04-21T15:12:33",
  "git_sha": "07e0217",
  "task_id": "stan.ingarch",
  "model": "claude-opus-4-7",
  "variant": "with_refs",
  "trial_n": 0,
  "seed": 42,
  "wall_clock_s": 312.4,
  "subprocess_exit": 0,
  "status": "completed",        // or "timeout", "crashed"
  "stdout_path": "eval/results/<run_id>/trial-<id>.stdout",
  "stderr_path": "eval/results/<run_id>/trial-<id>.stderr",
  "metrics": {
    "compiles": true,
    "fits": true,
    "divergences": 0,
    "max_rhat": 1.003,
    "min_ess": 650,
    "param_recovery_90ci": 0.77,
    "ppc_mean_diff": 0.12,
    "attempts": 1
  },
  "python_version": "3.13.11",
  "claude_code_version": "2.1.90"
}
```

Append-only. Crashes recorded as results with `status != "completed"`.

## StanScorer

Plain class, no abstract protocol (per fixed-point/no-premature-abstraction). Future domain scorers (pandas, numpy) will be new classes; we'll extract a common interface only when we need it.

```python
class StanScorer:
    def __init__(self, expected_params: list[str], data_simulator: Callable):
        self.expected_params = expected_params
        self.data_simulator = data_simulator

    def score(self, trial_dir: Path) -> dict:
        model_path = trial_dir / "model.stan"
        if not model_path.exists():
            return {"compiles": False, "fits": False, "status": "no_model"}
        # compile via cmdstanpy
        # simulate data, fit, collect diagnostics
        # check param recovery, PPC
        return {...}
```

Scorer does NOT read the reference library. Its inputs are: the task's expected params, the trial directory contents, and the output of running the model. Enforced by not passing `reference/` into the scorer's scope.

## Parallelism

Configurable via `--parallel N`, default `1`. Stan internally parallelizes 4 chains per trial; running multiple trials concurrently fights for the same CPU cores. We verify correctness sequentially first, then tune.

## Pilot run (first real execution)

`2 tasks × 2 models × 2 variants × 3 trials = 24 trials`, ~2 hours wall-clock at ~5 min/trial.

- Tasks: INGARCH (ported from `test_stan/`), GP mixture (ported from `test_stan/`)
- Models: `claude-opus-4-7`, `claude-sonnet-4-6`
- Variants: `with_refs`, `without_refs`
- Trials per cell: 3

Goal is correctness of the harness, not statistical significance. Expand only after the pilot JSONL looks sane.

## What this document does NOT cover

Left for later decisions, tracked in `ongoing_issues.md`:

- Cross-domain tasks (pandas, numpy) — after Stan works
- Generic `Scorer` protocol — after we have 2+ domain scorers
- SDK-based runner — after API access
- Statistical analysis procedure — deferred to Task #14

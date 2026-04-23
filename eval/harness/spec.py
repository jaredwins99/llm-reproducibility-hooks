"""Dataclasses for task specs and trial results.

TaskSpec: describes a single evaluation task. Same spec used across variants and models.
TrialResult: what gets written to the JSONL results file, one per trial.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable


# A scorer is any callable that takes a trial directory and returns a metrics dict.
# Kept as a type alias rather than a formal Protocol — we only have one scorer (StanScorer)
# and will extract an abstract interface only when we add a second domain (e.g. pandas).
Scorer = Callable[[Path], dict[str, Any]]


@dataclass(frozen=True)
class TaskSpec:
    """Describes one evaluation task.

    The same TaskSpec is used for every (model, variant, trial) combination.
    The `prompt` field is delivered byte-for-byte identically across variants —
    variant isolation happens via filesystem materialization, not prompt tweaks.
    """

    id: str
    """Unique identifier, e.g. 'stan.ingarch'. Used in result rows and filenames."""

    prompt: str
    """The task prompt given to Claude. Identical across variants."""

    initial_files: dict[str, str] = field(default_factory=dict)
    """Files to create in the trial dir before Claude runs. Filename -> contents.
    Keys are paths relative to the trial dir."""

    scorer: Scorer | None = None
    """Callable that computes metrics from a completed trial directory.
    None means the trial is not scored (useful for harness smoke tests)."""

    timeout_s: int = 1800
    """Hard wall-clock cap for the Claude subprocess. Enforced via subprocess timeout."""

    expected_duration_s: int = 600
    """Typical duration for a trial. Used for compute-budget estimates, not enforcement."""


@dataclass
class TrialResult:
    """One completed trial. Serialized as a single JSONL line.

    `status` encodes the outcome at the subprocess layer:
      - 'completed': subprocess exited (any exit code); scoring may or may not have run
      - 'timeout':   subprocess killed for exceeding TaskSpec.timeout_s
      - 'crashed':   harness itself raised before/during subprocess invocation
    """

    run_id: str
    trial_id: str
    timestamp: str
    git_sha: str
    task_id: str
    model: str
    variant: str
    iteration_mode: str
    trial_n: int
    seed: int
    wall_clock_s: float
    subprocess_exit: int | None
    status: str
    stdout_path: str
    stderr_path: str
    metrics: dict[str, Any]
    python_version: str
    claude_code_version: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

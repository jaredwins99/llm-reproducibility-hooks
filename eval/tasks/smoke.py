"""Smoke task — minimal task used to validate the harness end-to-end.

Not a real Stan task. Just asks the fake claude to create a marker file,
and scores whether it appeared. Used by the pilot smoke test, not real runs.
"""
from __future__ import annotations

from pathlib import Path

from eval.harness.spec import TaskSpec
from eval.tasks import register


def _score(trial_dir: Path) -> dict:
    marker = trial_dir / "solution.stan"
    return {
        "solution_written": marker.exists(),
        "size_bytes": marker.stat().st_size if marker.exists() else 0,
    }


TASK = register(TaskSpec(
    id="smoke.hello",
    prompt="Create a file named solution.stan with any content.",
    initial_files={"task.md": "# smoke task\nCreate solution.stan."},
    scorer=_score,
    timeout_s=30,
    expected_duration_s=5,
))

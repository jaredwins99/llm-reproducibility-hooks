"""Task registry. Tasks self-register via the REGISTRY dict.

Import a task module to make its TASK available:
    from eval.tasks import stan  # noqa — triggers registration

Or look up by id:
    spec = get_task("stan.ingarch")
"""
from __future__ import annotations

from eval.harness.spec import TaskSpec

REGISTRY: dict[str, TaskSpec] = {}


def register(spec: TaskSpec) -> TaskSpec:
    """Register a task. Returns the spec so it can be used as a decorator-like call."""
    if spec.id in REGISTRY:
        raise ValueError(f"duplicate task id: {spec.id}")
    REGISTRY[spec.id] = spec
    return spec


def get_task(task_id: str) -> TaskSpec:
    if task_id not in REGISTRY:
        raise KeyError(f"unknown task id {task_id!r}; known: {sorted(REGISTRY)}")
    return REGISTRY[task_id]


def all_tasks() -> list[TaskSpec]:
    return list(REGISTRY.values())

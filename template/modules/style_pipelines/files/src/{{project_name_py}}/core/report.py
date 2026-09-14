"""Per-step change reporting for pipeline stages.

Complements core.pipeline.log_step and the .px accessor, which report a shape
at a point in a chain. Stage reports the delta between steps: rows in, rows
out, and what moved. A stage that writes an artifact without calling one of
these is rejected by correctness/checks/check_pipelines.py.
"""

from __future__ import annotations

RULE = '  ' + '-' * 72


def report(label: str, frame) -> None:
    """Print a stage's resulting shape."""
    print(f'  {label:<28}{len(frame):>10,} rows x {len(frame.columns):>3} cols')


def note(label: str, detail: str) -> None:
    """Print a diagnostic that changes no data."""
    print(f'  {label:<28}{detail}')


class Stage:
    """Runs steps in sequence and reports the row and column change of each."""

    def __init__(self, label: str, frame):
        self.label = label
        self.frame = frame
        self.start = (len(frame), len(frame.columns))
        print(f'\n{label}')
        print(f'  {"input":<28}{len(frame):>10,} rows x {len(frame.columns):>3} cols')
        print(RULE)

    def step(self, label: str, fn, **kwargs):
        """Apply fn(frame, **kwargs) and report what changed."""
        before = (len(self.frame), len(self.frame.columns))
        self.frame = fn(self.frame, **kwargs)
        after = (len(self.frame), len(self.frame.columns))
        shift = f'cols {before[1]} -> {after[1]}' if after[1] != before[1] else ''
        print(f'  {label:<28}{before[0]:>10,} ->{after[0]:>10,}'
              f'{after[0] - before[0]:>+8,}   {shift}')
        return self.frame

    def note(self, label: str, detail: str) -> None:
        """Record a finding that changes nothing."""
        note(label, detail)

    def finish(self):
        """Print the stage total and return the frame."""
        print(RULE)
        rows, cols = len(self.frame), len(self.frame.columns)
        print(f'  {"output":<28}{rows:>10,} rows x {cols:>3} cols'
              f'   ({rows - self.start[0]:+,} rows, {cols - self.start[1]:+d} cols)')
        return self.frame

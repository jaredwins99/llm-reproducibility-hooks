"""Tests for the pipeline style gate.

Each test writes a fixture, runs the checker against it, and asserts which
rules fire. The evasion tests exist because the first implementation gated on
variable names and was defeated by renaming the frame.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parents[1] / 'checks' / 'check_pipelines.py'


def run_checker(target: Path) -> tuple[int, str]:
    """Run the gate against one file and return its status and report."""
    done = subprocess.run([sys.executable, str(CHECKER), str(target)],
                          capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def write(tmp_path: Path, name: str, body: str) -> Path:
    """Write a fixture file and return its path."""
    target = tmp_path / name
    target.write_text(body, encoding='utf-8')
    return target


CLEAN = '''"""A compliant pipeline."""
import pandas as pd


def drop_blanks(frame):
    """Remove empty rows."""
    return frame.dropna()


def main(path, out):
    """Read, chain, report, write."""
    frame = pd.read_parquet(path).pipe(drop_blanks).assign(n=1)
    report(frame)
    frame.to_parquet(out)
'''

ALL_FOUR = '''import pandas as pd


def bad(path, out):
    frame = pd.read_parquet(path)  # explain the thing
    frame = frame.dropna()
    frame = frame.head(10)
    frame["flag"] = 1
    frame.to_parquet(out)
'''

RENAMED = '''"""Evasion by renaming the frame."""
import pandas as pd


def sneaky(path, out):
    """No name hints anywhere."""
    q = pd.read_parquet(path)
    q = q.dropna()
    q = q.head(10)
    q.to_parquet(out)
'''

REAL_DICT = '''"""A genuine dict must not be treated as a frame."""


def configure(cfg):
    """Set a key."""
    cfg["key"] = 1
    return cfg
'''

DIRECTIVES = '''"""Tool directives are not commentary."""
import os  # noqa: F401
import sys  # type: ignore
import io  # noqa
'''

SMUGGLED = '''"""Prose smuggled after a directive."""
import json  # noqa: this drops the blanks because upstream is messy
'''


def test_clean_file_passes(tmp_path):
    """Compliant code exits zero."""
    code, _ = run_checker(write(tmp_path, 'clean.py', CLEAN))
    assert code == 0


@pytest.mark.parametrize('rule', ['PIPE001', 'PIPE002', 'PIPE003', 'PIPE004'])
def test_each_rule_fires(tmp_path, rule):
    """A file violating everything reports every rule."""
    code, report = run_checker(write(tmp_path, 'bad.py', ALL_FOUR))
    assert code == 1
    assert rule in report


def test_renaming_the_frame_does_not_evade(tmp_path):
    """Frame detection uses usage evidence, not variable names."""
    code, report = run_checker(write(tmp_path, 'renamed.py', RENAMED))
    assert code == 1
    assert 'PIPE002' in report


def test_a_real_dict_is_not_flagged(tmp_path):
    """Subscript assignment on a non-frame is legitimate."""
    code, report = run_checker(write(tmp_path, 'cfg.py', REAL_DICT))
    assert code == 0
    assert 'PIPE003' not in report


def test_tool_directives_are_allowed(tmp_path):
    """noqa and type comments are directives, not commentary."""
    code, _ = run_checker(write(tmp_path, 'directives.py', DIRECTIVES))
    assert code == 0


def test_prose_after_a_directive_is_reported(tmp_path):
    """A directive cannot hide a comment, though comments only advise."""
    code, report = run_checker(write(tmp_path, 'smuggled.py', SMUGGLED))
    assert code == 0
    assert 'PIPE001' in report


def test_comments_advise_but_do_not_block(tmp_path):
    """An inline comment is reported and the gate still passes."""
    body = CLEAN.replace('    return frame.dropna()',
                         '    return frame.dropna()  # drop blanks')
    code, report = run_checker(write(tmp_path, 'commented.py', body))
    assert code == 0
    assert 'advisory' in report


def test_strict_blocks_on_comments(tmp_path):
    """--strict turns advisory findings into failures."""
    target = write(tmp_path, 'smuggled.py', SMUGGLED)
    done = subprocess.run([sys.executable, str(CHECKER), '--strict', str(target)],
                          capture_output=True, text=True)
    assert done.returncode == 1


def test_unparseable_file_fails_closed(tmp_path):
    """A syntax error blocks, and reports rather than raising."""
    code, report = run_checker(write(tmp_path, 'broken.py', 'def broken(\n'))
    assert code == 1
    assert 'PIPE000' in report
    assert 'Traceback' not in report

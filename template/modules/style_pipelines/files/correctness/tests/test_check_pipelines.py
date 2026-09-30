"""Tests for the pipeline style gate.

Each test writes a fixture, runs the checker against it, and asserts which
rules fire. The evasion tests exist because the first implementation gated on
variable names and was defeated by renaming the frame. The last tests cover
writes through .loc, .iloc, .at and .iat, and paths the gate cannot check.
The checker is found where the module scaffolds it (correctness/checks/) or
where repro_stack vendors it (tools/), so a project runs this file unchanged.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = next(path for path in (Path(__file__).resolve().parents[1] / 'checks' / 'check_pipelines.py',
                                 Path(__file__).resolve().parents[1] / 'tools' / 'check_pipelines.py')
               if path.exists())


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


COPIED_SLICE = '''"""A frame known only from its columns, sliced, copied, then mutated."""


def screen(windowed, returning):
    """No reader and no frame method on the name that is mutated."""
    new_items = windowed[~windowed["item_name"].isin(returning)].copy()
    new_items["category"] = new_items["item_name"].map({})
    return new_items
'''

LATE_EVIDENCE = '''"""The evidence that source is a frame comes after the alias is mutated."""


def late(source):
    """Walk order must not decide whether the alias is a frame."""
    alias = source
    alias["flag"] = 1
    return source.dropna()
'''


SEPARATE_SCOPES = '''"""A lambda parameter is a frame in one function only."""


def pick(frame, keep):
    """f is a frame inside this lambda and nowhere else."""
    return frame.loc[lambda f: f["item_name"].isin(keep)]


def tally(items):
    """A dict built from a loop variable that happens to share the name."""
    values = {f: 0 for f in items}
    values["total"] = len(items)
    return values
'''


def test_frame_evidence_does_not_leak_between_scopes(tmp_path):
    """Evidence in one function does not make a same-named dict a frame in another."""
    code, report = run_checker(write(tmp_path, 'scopes.py', SEPARATE_SCOPES))
    assert code == 0
    assert 'PIPE003' not in report


def test_frame_known_from_column_access_is_caught(tmp_path):
    """Taking a column and using it as a Series is evidence of a frame."""
    code, report = run_checker(write(tmp_path, 'copied.py', COPIED_SLICE))
    assert code == 1
    assert 'PIPE003' in report


def test_evidence_after_the_mutation_is_still_used(tmp_path):
    """Frame evidence propagates through assignments regardless of order."""
    code, report = run_checker(write(tmp_path, 'late.py', LATE_EVIDENCE))
    assert code == 1
    assert 'PIPE003' in report


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


AT_WRITES = '''"""Cell writes on a name with no other evidence of being a frame."""


def fill(table, rows, cells):
    """Each write goes through an indexer only pandas objects have."""
    copied = table.copy()
    for row, column in rows:
        copied.at[row, column] = 'yes'
    for row, column in cells:
        copied.iat[row, column] = 'no'
    return copied
'''


def test_writes_through_at_and_iat_are_caught_without_other_evidence(tmp_path):
    """.at and .iat exist only on pandas objects, so a write through them is in place."""
    code, report = run_checker(write(tmp_path, 'cells.py', AT_WRITES))
    assert code == 1
    assert "'copied.at[...] = ...'" in report
    assert "'copied.iat[...] = ...'" in report


def test_a_write_through_loc_is_caught_on_a_name_known_only_by_it(tmp_path):
    """A .loc write needs no frame method elsewhere to be recognised."""
    body = 'def set_flag(table, where):\n    table.loc[where, "flag"] = 1\n    return table\n'
    code, report = run_checker(write(tmp_path, 'loc.py', body))
    assert code == 1
    assert "'table.loc[...] = ...'" in report


def test_reading_through_at_is_not_a_write(tmp_path):
    """Only an assignment through the indexer is reported."""
    body = 'def first(table):\n    return table.at[0, "x"]\n'
    code, report = run_checker(write(tmp_path, 'read.py', body))
    assert code == 0
    assert 'PIPE003' not in report


def test_a_file_that_is_not_python_is_warned_about_not_passed_over(tmp_path):
    """A path the gate cannot read says so on stderr instead of passing silently."""
    code, report = run_checker(write(tmp_path, 'fit.R', 'x <- 1\n'))
    assert code == 0
    assert 'WARNING' in report and 'fit.R is not a Python file' in report


def test_a_folder_with_no_python_is_warned_about(tmp_path):
    """A gated folder holding nothing to check is reported, so a wrong GATE_DIRS shows."""
    (tmp_path / 'empty').mkdir()
    code, report = run_checker(tmp_path / 'empty')
    assert code == 0
    assert 'holds no Python files' in report


def test_a_path_that_does_not_exist_fails_closed(tmp_path):
    """A misspelt path would otherwise gate nothing and pass."""
    code, report = run_checker(tmp_path / 'nowhere')
    assert code == 1
    assert 'PIPE000' in report and 'does not exist' in report

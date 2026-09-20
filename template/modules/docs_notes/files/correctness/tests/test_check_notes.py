"""The notes check fails on each way a note can stop being trustworthy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'checks'))

import check_notes as check  # noqa: E402


def repo(tmp_path: Path, *, directories: str = 'src', registries: str = '') -> Path:
    """A repository with one source file and an empty notes directory."""
    subprocess.run(['git', 'init', '-q'], cwd=tmp_path, check=True)
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'work.py').write_text('x = 1\n', encoding='utf-8')
    (tmp_path / 'notes' / 'decisions').mkdir(parents=True)
    (tmp_path / 'notes' / 'coverage.ini').write_text(
        '[coverage]\n'
        f'directories = {directories}\n'
        'suffixes = .py, .R, .sh\n'
        'exclude = */tests/*, tests/*, */__init__.py\n'
        f'registries = {registries}\n', encoding='utf-8')
    return tmp_path


def note(root: Path, name: str, *, kind: str = 'decision', covers: str = 'src/work.py',
         claim: str = '', evidence: str = '') -> Path:
    path = root / 'notes' / 'decisions' / f'{name}.md'
    path.write_text(f'---\nkind: {kind}\ntitle: {name}\ncovers: {covers}\n'
                    + (f'claim: {claim}\n' if claim else '')
                    + (f'evidence: {evidence}\n' if evidence else '')
                    + '---\nwhy\n', encoding='utf-8')
    return path


def test_a_covered_source_file_passes(tmp_path):
    root = repo(tmp_path)
    note(root, 'work')
    assert check.main(['--root', str(root)]) == 0
    assert 'work' in (root / 'notes' / 'INDEX.md').read_text(encoding='utf-8')


def test_a_source_file_no_note_covers_fails(tmp_path, capsys):
    root = repo(tmp_path)
    assert check.main(['--root', str(root)]) == 1
    assert 'uncovered: src/work.py' in capsys.readouterr().out


def test_a_note_covering_a_deleted_file_fails(tmp_path, capsys):
    root = repo(tmp_path)
    note(root, 'work')
    note(root, 'gone', covers='src/gone.py')
    assert check.main(['--root', str(root)]) == 1
    assert 'does not exist' in capsys.readouterr().out


def test_two_decisions_on_one_file_fail(tmp_path, capsys):
    root = repo(tmp_path)
    note(root, 'first')
    note(root, 'second')
    assert check.main(['--root', str(root)]) == 1
    assert 'is decided by' in capsys.readouterr().out


def test_a_finding_whose_evidence_stops_showing_its_claim_fails(tmp_path, capsys):
    root = repo(tmp_path)
    note(root, 'work')
    note(root, 'counted', kind='finding', covers='src/work.py', claim='7 rows', evidence='echo 7 rows')
    assert check.main(['--root', str(root), '--evidence']) == 0
    note(root, 'counted', kind='finding', covers='src/work.py', claim='7 rows', evidence='echo 8 rows')
    assert check.main(['--root', str(root), '--evidence']) == 1
    assert 'no longer shows' in capsys.readouterr().out


def test_a_finding_whose_evidence_command_fails_is_reported(tmp_path, capsys):
    root = repo(tmp_path)
    note(root, 'work')
    note(root, 'broken', kind='finding', covers='src/work.py', claim='x', evidence='exit 3')
    assert check.main(['--root', str(root), '--evidence']) == 1
    assert 'evidence failed' in capsys.readouterr().out


def test_the_scope_is_read_from_the_config_not_hardcoded(tmp_path):
    """A directory or a language left out of coverage.ini is the one way code escapes."""
    root = repo(tmp_path, directories='src, tools')
    (root / 'tools').mkdir()
    (root / 'tools' / 'helper.R').write_text('x <- 1\n', encoding='utf-8')
    note(root, 'work')
    assert check.main(['--root', str(root)]) == 1
    note(root, 'helper', covers='tools/helper.R')
    assert check.main(['--root', str(root)]) == 0


def test_tests_are_not_required_to_be_covered(tmp_path):
    root = repo(tmp_path)
    (root / 'src' / 'tests').mkdir()
    (root / 'src' / 'tests' / 'test_work.py').write_text('def test_x(): pass\n', encoding='utf-8')
    note(root, 'work')
    assert check.main(['--root', str(root)]) == 0


def test_a_registry_counts_as_coverage(tmp_path, monkeypatch):
    """A project that documents its modules elsewhere need not repeat them in a note."""
    root = repo(tmp_path, registries='catalog:MODULES')
    (root / 'catalog.py').write_text('MODULES = ["src/work.py"]\n', encoding='utf-8')
    monkeypatch.syspath_prepend(str(root))
    assert check.main(['--root', str(root)]) == 0


def test_a_note_without_frontmatter_or_with_an_unknown_kind_is_refused(tmp_path):
    root = repo(tmp_path)
    (root / 'notes' / 'decisions' / 'bare.md').write_text('no frontmatter\n', encoding='utf-8')
    try:
        check.main(['--root', str(root)])
    except ValueError as error:
        assert 'no frontmatter' in str(error)
    else:
        raise AssertionError('a note without frontmatter should be refused')

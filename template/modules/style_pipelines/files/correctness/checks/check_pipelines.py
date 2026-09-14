"""Deterministic gate for the pandas-pipeline style.

Exits non-zero on any violation so it can be wired into a PreToolUse hook,
a pre-commit hook and CI without behaving differently in any of them.

Rules
-----
PIPE001  inline comment (advisory: reported, blocks only under --strict)
PIPE002  sequential reassignment of one name instead of a pipe chain
PIPE003  in-place column mutation instead of .assign()
PIPE004  a stage writes an artifact without reporting shape first
"""

from __future__ import annotations

import argparse
import ast
import io
import sys
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path

DIRECTIVE = re.compile(
    r"^(noqa(:\s*[A-Z]+[0-9]+(\s*,\s*[A-Z]+[0-9]+)*)?"
    r"|type:\s*(ignore(\[[^\]]+\])?|[\w\.\[\], ]+)"
    r"|pragma:\s*no\s?cover)$",
    re.IGNORECASE)

ENFORCED = {"PIPE000", "PIPE002", "PIPE003", "PIPE004"}
ADVISORY = {"PIPE001"}

WRITERS = {"to_parquet", "to_csv", "to_feather", "to_pickle", "to_excel"}
REPORTERS = {"report", "step", "note", "validate", "describe_change",
             "log_step", "log", "val", "px", "finish", "Stage"}
FRAME_METHODS = {
    "pipe", "assign", "query", "groupby", "merge", "dropna", "drop_duplicates",
    "rename", "reset_index", "set_index", "sort_values", "fillna", "astype",
    "head", "tail", "loc", "iloc", "to_parquet", "to_csv", "value_counts",
}
FRAME_READERS = {"read_parquet", "read_csv", "read_excel", "DataFrame", "concat"}


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    code: str
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.message}"


def frame_names(tree: ast.AST) -> set[str]:
    """Names with positive evidence of being a DataFrame, from usage not naming."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in FRAME_METHODS:
            root = node.value
            if isinstance(root, ast.Name):
                names.add(root.id)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            for inner in ast.walk(node.value):
                if isinstance(inner, ast.Attribute) and inner.attr in FRAME_READERS:
                    names.add(target.id)
                if isinstance(inner, ast.Name) and inner.id in names:
                    names.add(target.id)
    return names


def _attribute_root(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Call, ast.Subscript)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


def find_inline_comments(path: Path, source: str) -> list[Violation]:
    found = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            text = token.string.lstrip("#").strip()
            if text.startswith("!") or text.startswith("-*-"):
                continue
            if DIRECTIVE.match(text):
                continue
            found.append(Violation(path, token.start[0], "PIPE001",
                                   "inline comment; put the reasoning in the review page"))
    return found


def find_sequential_reassignment(path: Path, tree: ast.AST) -> list[Violation]:
    found = []
    frames = frame_names(tree)
    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        counts: dict[str, list[int]] = {}
        for stmt in scope.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue
            if _attribute_root(stmt.value) != target.id:
                continue
            if target.id not in frames:
                continue
            counts.setdefault(target.id, []).append(stmt.lineno)
        for name, lines in counts.items():
            if len(lines) >= 2:
                found.append(Violation(path, lines[1], "PIPE002",
                                       f"'{name}' reassigned from itself {len(lines)} times; "
                                       f"chain these with .pipe()"))
    return found


def find_inplace_mutation(path: Path, tree: ast.AST) -> list[Violation]:
    found = []
    frames = frame_names(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Subscript):
                continue
            root = _attribute_root(target)
            if root in frames:
                found.append(Violation(path, node.lineno, "PIPE003",
                                       f"'{root}[...] = ...' mutates in place; use .assign()"))
    return found


def find_unreported_writes(path: Path, tree: ast.AST) -> list[Violation]:
    found = []
    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls = [n for n in ast.walk(scope) if isinstance(n, ast.Call)]
        names = {n.func.attr for n in calls if isinstance(n.func, ast.Attribute)}
        names |= {n.func.id for n in calls if isinstance(n.func, ast.Name)}
        writes = names & WRITERS
        if writes and not (names & REPORTERS):
            line = next(n.lineno for n in calls
                        if isinstance(n.func, ast.Attribute) and n.func.attr in writes)
            found.append(Violation(path, line, "PIPE004",
                                   f"writes an artifact with no shape reported before it"))
    return found


def check_file(path: Path) -> list[Violation]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [Violation(path, exc.lineno or 1, "PIPE000",
                          f"file does not parse: {exc.msg}")]
    return (find_inline_comments(path, source)
            + find_sequential_reassignment(path, tree)
            + find_inplace_mutation(path, tree)
            + find_unreported_writes(path, tree))


def collect(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        out.extend(sorted(p.rglob("*.py")) if p.is_dir() else [p])
    return [p for p in out if p.suffix == ".py"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["src", "scripts"])
    parser.add_argument("--select", default="", help="comma-separated codes to report")
    parser.add_argument("--strict", action="store_true",
                        help="also fail on advisory codes")
    args = parser.parse_args(argv)

    selected = {c for c in args.select.split(",") if c} or None
    findings = [v for p in collect(args.paths or ["src", "scripts"])
                for v in check_file(p)
                if selected is None or v.code in selected]
    blocking = ENFORCED | (ADVISORY if args.strict else set())
    violations = [v for v in findings if v.code in blocking]
    advice = [v for v in findings if v.code not in blocking]

    for v in sorted(violations, key=lambda v: (str(v.path), v.line)):
        print(v.render(), file=sys.stderr)
    for v in sorted(advice, key=lambda v: (str(v.path), v.line)):
        print(f"{v.render()}  (advisory)", file=sys.stderr)

    if advice:
        print(f"\n{len(advice)} advisory finding(s), not blocking", file=sys.stderr)
    if violations:
        counts: dict[str, int] = {}
        for v in violations:
            counts[v.code] = counts.get(v.code, 0) + 1
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"\n{len(violations)} violation(s): {summary}", file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())

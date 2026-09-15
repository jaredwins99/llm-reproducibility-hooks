"""Keep dvc.yaml in step with the make pipeline.

project.mk lists the pipeline in order (PIPELINE_PY, then PIPELINE_R) and
every dvc.yaml stage runs one entry of it through make. Without --check this
prints dvc.yaml stages for the make pipeline; with --check it exits 1 when
dvc.yaml runs other commands than the make pipeline or runs them in another
order.

    python tools/dvc_stages.py --py "$(PIPELINE_PY)" --r "$(PIPELINE_R)"
    python tools/dvc_stages.py --check --py "..." --r "..."
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def make_command(kind: str, step: str) -> str:
    """The make invocation that runs one pipeline entry."""
    if kind == "py":
        return f"make -s step M={step}"
    return f"make -s pipeline-r PIPELINE_R={step}"


def stage_name(step: str) -> str:
    """Stage name from a script path or module name, without its order prefix."""
    stem = Path(step).stem if step.endswith((".py", ".R", ".r")) else step.rsplit(".", 1)[-1]
    return re.sub(r"^\d+_", "", stem)


def step_file(kind: str, step: str) -> str:
    """The file a pipeline entry runs."""
    if kind == "py" and not step.endswith(".py"):
        return "src/" + step.replace(".", "/") + ".py"
    return step


def pipeline(py: str, r: str) -> list[tuple[str, str]]:
    """Make pipeline entries in run order."""
    return [("py", s) for s in py.split()] + [("r", s) for s in r.split()]


def dvc_commands(path: Path) -> list[str]:
    """Stage commands in dvc.yaml, in file order; commented lines are ignored."""
    if not path.exists():
        return []
    return [m.group(1).strip().strip("'\"")
            for m in re.finditer(r"^[ \t]*cmd:[ \t]*(.+)$", path.read_text(encoding="utf-8"), re.M)]


def skeleton(steps: list[tuple[str, str]]) -> str:
    """dvc.yaml stages for the pipeline, with deps and outs to complete."""
    lines = ["stages:"]
    for kind, step in steps:
        lines += [f"  {stage_name(step)}:",
                  f"    cmd: {make_command(kind, step)}",
                  "    deps:",
                  f"      - {step_file(kind, step)}",
                  "      - src" if kind == "py" else "      - R",
                  "      - config",
                  "    outs:",
                  "      - data/TODO"]
    return "\n".join(lines) if steps else "stages: {}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--py", default="", help="PIPELINE_PY from project.mk")
    parser.add_argument("--r", default="", help="PIPELINE_R from project.mk")
    parser.add_argument("--dvc-file", default="dvc.yaml")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    steps = pipeline(args.py, args.r)
    if not args.check:
        print(skeleton(steps))
        return 0

    expected = [make_command(kind, step) for kind, step in steps]
    actual = dvc_commands(Path(args.dvc_file))
    if actual == expected:
        print(f"dvc.yaml matches the make pipeline ({len(expected)} stage(s))")
        return 0
    print(f"{args.dvc_file} does not run the make pipeline in project.mk order", file=sys.stderr)
    print("  project.mk: " + (" | ".join(expected) or "(empty)"), file=sys.stderr)
    print("  dvc.yaml:   " + (" | ".join(actual) or "(no stages)"), file=sys.stderr)
    print("  regenerate the stages with: make dvc-stages", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

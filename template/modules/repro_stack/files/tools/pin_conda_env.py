"""Write environment.yml pinned to exactly the third-party packages the code imports.

Scans the given source directories for imports, drops the standard library
and the project's own packages, maps import names to conda package names,
and pins each to the version installed in a reference conda environment.

    python tools/pin_conda_env.py --prefix ~/miniconda3/envs/work \
        --name hens --dirs src scripts tests --local hens \
        --extra cmdstanpy=1.2.5 --extra pre-commit=4.3.0 \
        --python 3.9.23 > environment.yml

Packages that are imported but not installed in the reference environment
are listed on stderr and make the script exit non-zero, so an unpinned
dependency cannot slip through.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import sysconfig
from pathlib import Path

IMPORT_TO_CONDA = {
    "yaml": "pyyaml",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "cv2": "opencv",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "skimage": "scikit-image",
    "google": "protobuf",
    "attr": "attrs",
    "dotenv": "python-dotenv",
    "jwt": "pyjwt",
    "Bio": "biopython",
}

FALLBACK_STDLIB = {
    "__future__", "abc", "argparse", "array", "ast", "asyncio", "base64", "bisect",
    "calendar", "collections", "concurrent", "configparser", "contextlib", "copy",
    "csv", "ctypes", "dataclasses", "datetime", "decimal", "difflib", "email", "enum",
    "errno", "fnmatch", "fractions", "functools", "gc", "getpass", "glob", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "importlib", "inspect", "io",
    "ipaddress", "itertools", "json", "keyword", "logging", "lzma", "math",
    "mimetypes", "multiprocessing", "numbers", "operator", "os", "pathlib", "pickle",
    "platform", "pprint", "queue", "random", "re", "secrets", "select", "shlex",
    "shutil", "signal", "socket", "sqlite3", "ssl", "stat", "statistics", "string",
    "struct", "subprocess", "sys", "sysconfig", "tarfile", "tempfile", "textwrap",
    "threading", "time", "timeit", "tokenize", "traceback", "types", "typing",
    "unicodedata", "unittest", "urllib", "uuid", "warnings", "weakref", "webbrowser",
    "xml", "zipfile", "zlib", "zoneinfo",
}


def stdlib_names() -> set[str]:
    """Standard-library top-level module names for the running interpreter."""
    names = set(getattr(sys, "stdlib_module_names", ())) | set(sys.builtin_module_names)
    stdlib = Path(sysconfig.get_paths()["stdlib"])
    names |= {p.stem for p in stdlib.glob("*.py")}
    names |= {p.name for p in stdlib.iterdir() if (p / "__init__.py").exists()}
    return names | FALLBACK_STDLIB


def imports_in(path: Path) -> set[str]:
    """Top-level absolute import names in one Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


def local_names(dirs: list[Path]) -> set[str]:
    """Modules and packages that live inside the scanned directories."""
    names = set()
    for d in dirs:
        names |= {p.stem for p in d.rglob("*.py")}
        names |= {p.parent.name for p in d.rglob("__init__.py")}
    return names


def installed(prefix: str) -> dict[str, tuple[str, str]]:
    """Package name to (version, channel) in a conda environment; pip installs report channel "pypi"."""
    listing = subprocess.run(["conda", "list", "--json", "-p", prefix],
                             capture_output=True, text=True, check=True)
    return {rec["name"].lower(): (rec["version"], rec.get("channel", ""))
            for rec in json.loads(listing.stdout)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prefix", required=True, help="reference conda environment")
    parser.add_argument("--name", required=True, help="environment name to write")
    parser.add_argument("--dirs", nargs="+", default=["src", "scripts", "tests"])
    parser.add_argument("--local", nargs="*", default=[], help="project package names")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="import names to leave out (private or pip-only packages)")
    parser.add_argument("--extra", action="append", default=[],
                        help="name or name=version added whether imported or not")
    parser.add_argument("--pip", action="append", default=[],
                        help="name==version installed with pip; packages the reference env got from PyPI go to pip automatically")
    parser.add_argument("--python", help="python version; default: the reference env's")
    parser.add_argument("--channel", default="conda-forge")
    args = parser.parse_args(argv)

    dirs = [Path(d) for d in args.dirs if Path(d).is_dir()]
    imported = set().union(*(imports_in(p) for d in dirs for p in d.rglob("*.py")))
    third_party = (imported - stdlib_names() - local_names(dirs)
                   - set(args.local) - set(args.exclude))
    versions = installed(args.prefix)

    pins, pip_pins, missing = {}, {}, []
    for name in sorted(third_party):
        conda_name = IMPORT_TO_CONDA.get(name, name).lower().replace("_", "-")
        record = versions.get(conda_name) or versions.get(conda_name.replace("-", "_"))
        if record is None:
            missing.append(f"{name} (conda package {conda_name})")
        elif record[1] == "pypi":
            pip_pins[conda_name] = record[0]
        else:
            pins[conda_name] = record[0]
    for extra in args.extra:
        name, _, version = extra.partition("=")
        pins[name] = version or versions.get(name, ("", ""))[0]
    for spec in args.pip:
        name, _, version = spec.partition("==")
        pip_pins[name.strip().lower()] = version
    pins = {n: v for n, v in pins.items() if n not in pip_pins}

    python = args.python or versions.get("python", ("", ""))[0]
    lines = [f"name: {args.name}", "channels:", f"  - {args.channel}", "  - nodefaults",
             "dependencies:", f"  - python={python}" if python else "  - python", "  - pip"]
    lines += [f"  - {n}={v}" if v else f"  - {n}" for n, v in sorted(pins.items())]
    if pip_pins:
        lines += ["  - pip:"] + [f"      - {n}=={v}" if v else f"      - {n}"
                                 for n, v in sorted(pip_pins.items())]
    print("\n".join(lines))
    print(f"excluded on request: {', '.join(sorted(args.exclude)) or 'none'}", file=sys.stderr)

    print(f"pinned {len(pins)} conda and {len(pip_pins)} pip package(s) from {len(imported)} imported name(s)", file=sys.stderr)
    for m in missing:
        print(f"  NOT INSTALLED in {args.prefix}: {m}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

# Python Linting Decisions

Record of all ruff rule categories evaluated and the decision for each.

## Enabled (all projects)

| Rule | Category | Why |
|---|---|---|
| E | pycodestyle errors | Consistent spacing, indentation, basic syntax |
| F | pyflakes | Unused imports, undefined names, dead code |
| W | pycodestyle warnings | Trailing whitespace, excessive blank lines |
| B | flake8-bugbear | Mutable defaults, bare except, == None |
| S | flake8-bandit | Hardcoded secrets, SQL injection, eval, shell=True |
| I | isort | Grouped, sorted imports (stdlib / third-party / local) |
| N | pep8-naming | snake_case functions, PascalCase classes, UPPER_CASE constants |
| UP | pyupgrade | Modern syntax: f-strings, union types, remove old patterns |
| A | flake8-builtins | Don't shadow builtins (list, id, type, input) |
| SIM | flake8-simplify | Simplify if/else, merge nested with-statements |
| PT | flake8-pytest-style | Enforce pytest idioms over unittest patterns |
| PERF | perflint | Generators over lists in sum(), dict.get over try/except |
| RUF | ruff-specific | Ruff's own rules (except RUF012) |
| C90 | mccabe | Max cyclomatic complexity = 10 |
| PLR | pylint refactor | Max 5 args, flag too many branches |
| PLW | pylint warnings | Unreachable code, dangerous defaults |
| PLE | pylint errors | Bad string formatting, invalid __all__ |

## Enabled (library/package projects only)

| Rule | Category | Why conditional |
|---|---|---|
| TCH | flake8-type-checking | Move type-only imports behind TYPE_CHECKING. Matters for library startup time, not for scripts/pipelines. |
| ANN | flake8-annotations | Require type hints on public APIs. Libraries need clear contracts; scripts/pipelines have complex data types (DataFrame, ndarray) that make annotations verbose. |
| D | pydocstyle (NumPy) | Require docstrings on public API. Libraries are consumed by others who need docs. Scripts/pipelines are self-contained — in the age of AI tools, excessive docstrings on non-library code is clutter. |

## Not enabled

| Rule | Category | Why not |
|---|---|---|
| C4 | flake8-comprehensions | User preference: explicit loops can be clearer than comprehensions in some cases. Don't force the rewrite. |
| ERA | eradicate | Flags commented-out code. While git has history, sometimes temporary comments during development are useful. Too aggressive for a default. |
| FIX | fixme | Flags TODO/FIXME comments. TODOs are a valid workflow tool — flagging them breaks `make lint` during active development. |
| TD | todo-format | Enforces specific TODO format (author, issue link). Too bureaucratic for most projects. |
| ARG | unused-arguments | Flags unused function args. Breaks callback patterns, interface implementations, and signal handlers where the signature is required. |
| DTZ | datetimez | Requires timezone-aware datetimes. Valid concern but too aggressive — many data pipelines work in UTC-only or local time legitimately. |
| PIE | misc | Miscellaneous simplifications. Overlaps heavily with SIM; enabling both is noisy with diminishing returns. |
| RET | return | Simplify return statements (no `else` after `return`). Matter of taste — some people find explicit else branches more readable. |
| FBT | boolean-trap | Flags boolean args in function signatures. Good principle but too many false positives (e.g., `verbose=True`). |
| TRY | tryceratops | Strict exception handling rules. Some are good but many are too opinionated (e.g., no broad `Exception` catch even when intentional). |
| EM | error-messages | Requires error messages be variables, not inline strings. Adds indirection for marginal benefit. |
| COM | trailing-commas | Enforce trailing commas in multiline structures. Handled by the formatter already. |
| Q | quotes | Quote consistency. Handled by the formatter already. |
| RSE | unnecessary-paren | Unnecessary parentheses on raised exceptions. Very minor. |
| SLF | self | Flags private member access from outside. Too strict for testing and data science workflows. |
| SLOT | slots | Enforce __slots__ on classes. Premature optimization for most code. |
| INP | implicit-namespace | Flags implicit namespace packages. Niche concern. |
| ISC | implicit-string-concat | Flags implicit string concatenation. Some false positives with multiline strings. |

## Specific rule ignores

| Rule | Why ignored |
|---|---|
| RUF012 | Requires `field(default_factory=list)` for mutable class variables. The `dataclasses.field()` pattern is overly verbose when a simple `items: list = []` is clear enough in context. The actual bug (shared mutable state) is better caught by B006. |

## Formatter settings

| Setting | Value | Why |
|---|---|---|
| line-length | 88 | ruff/black default, good balance |
| quote-style | single | User preference |
| target-version | py311 | Modern Python baseline |

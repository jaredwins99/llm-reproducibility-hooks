# The Forest — Decision Log

Complete record of every design decision made during the deep-dive sessions.

---

## 1. Framework Architecture

### The Five Tenets
Every file, folder, and decision maps to one of five tenets:
1. **Reproducibility** — Docker, env management, git, DVC, MLflow
2. **Correctness** — hooks, CI, testing, Claude-as-reviewer
3. **Legibility** — style guides, conventions, ADRs, Claude tooling, linter configs, IDE
4. **Observability** — logging, monitoring, change auditing
5. **Security** — secrets, permissions, dependency scanning, telemetry control

Five tenets match five decision trees — kept equal for memorability.

### The Five Decision Trees
| Tree | Type | Choices |
|---|---|---|
| 1. Project Type | multi-select | dataset (oneoff/pipeline-batch/streaming), model (classical/ml/llm-app/optimization), service (api/web/fullstack/cli), library |
| 2. Language | multi-select | Python (uv/conda), R (renv+rig) |
| 3. Infrastructure | multi-select | local, cloud (aws/gcp/azure), hpc |
| 4. Team Topology | single-select | solo, team |
| 5. Data Sensitivity | multi-select | public, internal, regulated |

### Module System
- 28 modules, each with `manifest.sh` + `files/` directory
- Resolver maps selections to active modules via activation conditions
- Accumulator files (.gitignore, Makefile, .pre-commit-config.yaml) merge across modules
- `.dev_template.lock` records selections for reproducible replay

### Generated Project Layout
- Root: only tool-required files (.gitignore, pyproject.toml, Makefile, CLAUDE.md, .github/, etc.)
- VS Code file nesting groups root files visually under principle folders
- Principle folders: `reproducibility/`, `correctness/`, `observability/`, `security/`, `legibility/`
- Content folders: `src/`, `scripts/`, `data/`, `models/`, `reports/` (conditional)
- No symlinks anywhere
- No empty placeholder folders for notebooks or scripts

### VS Code Nesting Groups
| Parent | Nests |
|---|---|
| `.gitignore` | .gitattributes, .dockerignore, .github |
| `reproducibility/` | pyproject.toml, uv.lock, .python-version, DESCRIPTION, renv.lock, Dockerfile, docker-compose.yml, .dev_template.lock |
| `correctness/` | .pre-commit-config.yaml |
| `legibility/` | ruff.toml, .lintr, CLAUDE.md, .claude/, .vscode/, README.md, Makefile |

### Post-Scaffold Auto-Setup
Interactive steps after scaffolding:
1. Git init + GitHub remote (with deploy key option + branch protection)
2. Docker registry login
3. DVC init + remote
4. MLflow tracking URI
5. Pre-commit install

---

## 2. The Library/Pipeline Split

A fundamental design axis: libraries are strict, everything else is lean.

| Aspect | Pipeline / Script / Service | Library / Package |
|---|---|---|
| Error handling | Let it crash with clear traceback | try/except at public API boundaries |
| Input validation | None — trust your own data | Validate all inputs |
| Type hints (ANN) | Not enforced | Enforced by ruff |
| Docstrings (D) | Not enforced | NumPy style, enforced by ruff |
| Type-checking imports (TCH) | Not enforced | Enforced by ruff |
| Imports | Broad — preamble with wildcard import | Explicit, minimal imports only |
| R libraries | `library(tidyverse)` OK | Explicit individual packages |
| Test stubs | Not auto-generated | Auto-generated for each module |
| Test requirements | Unit tests for `src/` functions + output schema checks | Every public function has a test |

---

## 3. Python Linting (ruff)

### Enabled Rules — All Projects
| Rule | Category | What it catches |
|---|---|---|
| E | pycodestyle errors | Spacing, indentation, syntax |
| F | pyflakes | Unused imports, undefined names |
| W | pycodestyle warnings | Trailing whitespace, blank lines |
| I | isort | Import sorting (stdlib / third-party / local) |
| N | pep8-naming | snake_case functions, PascalCase classes, UPPER_CASE constants |
| UP | pyupgrade | Modern syntax (f-strings, union types) |
| B | flake8-bugbear | Mutable defaults, bare except, == None |
| S | flake8-bandit | Hardcoded secrets, SQL injection, eval, shell=True |
| A | flake8-builtins | No shadowing builtins (list, id, type) |
| SIM | flake8-simplify | Simplify if/else, merge nested withs |
| PT | flake8-pytest-style | Enforce pytest idioms |
| PERF | perflint | Generators over lists, dict.get over try/except |
| RUF | ruff-specific | Ruff's own rules (except RUF012) |
| C90 | mccabe | Max cyclomatic complexity = 10 |
| PLR | pylint refactor | Max 5 args, too many branches |
| PLW | pylint warnings | Unreachable code |
| PLE | pylint errors | Bad formatting, invalid __all__ |

### Enabled Rules — Library Projects Only
| Rule | Category | Why conditional |
|---|---|---|
| TCH | type-checking imports | Library startup time matters |
| ANN | type annotations | Public APIs need clear contracts |
| D | pydocstyle (NumPy) | Library consumers need docs |

### Disabled Rules
| Rule | Why |
|---|---|
| C4 (comprehensions) | Explicit loops can be clearer; don't force |
| ERA (commented code) | Sometimes useful during development |
| FIX (fixme) | TODOs are a valid workflow tool |
| RUF012 | `field(default_factory=)` is overly verbose |

### Formatter Settings
| Setting | Value |
|---|---|
| line-length | 88 |
| quote-style | single |
| target-version | py311 |

### Per-File Ignores
- `correctness/tests/**`: allow assert (S101), magic values (PLR2004)
- `scripts/**`: allow assert (S101)

---

## 4. R Linting (lintr)

### Enabled Linters
| Linter | Setting |
|---|---|
| line_length_linter | 120 chars |
| object_name_linter | snake_case |
| assignment_linter | require `<-` |
| pipe_continuation_linter | pipe at end of line |
| brace_linter | `allow_single_line = TRUE` (closing brace on same line as last statement) |
| T_and_F_symbol_linter | require TRUE/FALSE |
| seq_linter | require seq_along() |
| undesirable_function_linter | flag sapply, subset, read.csv, write.csv |
| library_call_linter | all library() at top of file |
| cyclocomp_linter | max complexity = 15 |
| spaces_inside_linter | no spaces inside parens |

### Disabled
| Linter | Why |
|---|---|
| commented_code_linter | allow commented-out code |

### R-Specific Style Decisions
- **Pipe**: both `%>%` and `|>` allowed; prefer `%>%` when `.` placeholder is needed
- **Braces**: closing brace on same line as last statement (default, changeable). `} else {` must always be on one line (R parser requirement)
- **identity()**: always end pipe chains with `identity()` so any line can be commented out
- **Tidyverse preferred**: flag base R equivalents when tidyverse exists

---

## 5. Code Style (Both Languages)

### General Principles
- Code speaks for itself — if you need a comment to explain what, rename or refactor
- Move left: prefer declarative rules over runtime checks
- Defensiveness is conditional (see Library/Pipeline Split)
- Default to logging (saved to files), not print — Claude reads logs
- f-strings only (Python); no old-style formatting

### Comments
- **Extremely sparse** — the vast majority of code needs no inline comments
- **Allowed**: section separators, "why" comments, pipeline section labels
- **Rejected (by Claude hook)**: "what" comments that restate the code
- **Section separator format** (standardized, em dashes):
  ```
  # ———————————————————————————————————
  #      Section Title Here
  # ———————————————————————————————————
  ```

### Paths
Always OS-portable. Never hardcode `/` or `\\`.
- Python: `Path('data') / 'v001' / 'file.parquet'`
- R: `file.path('data', 'v001', 'file.parquet')`

### Constants
UPPER_CASE, grouped at the top of scripts after imports.

### Naming
- snake_case for functions, variables, modules (both languages)
- PascalCase for classes (Python)
- UPPER_CASE for constants (both languages)
- Pipeline scripts prefixed with numbers: `01_extract.py`, `02_transform.py`

---

## 6. Data Pipeline Style (Python & R)

Only applies to data/model project types. Nine rules:

### 1. Chains, not variables
Single continuous chain from input to output. No intermediate variables.

### 2. Bare pipeline at script level
The outermost pipeline is NOT wrapped in a function. This allows commenting out steps to debug interactively.

### 3. Extract functions only when needed
Base pandas/dplyr is legible. Extract into `.pipe()`-able functions only when a section exceeds ~10 operations, is reused, or needs its own tests. **Functions always live in `src/`, never in `scripts/`.**

### 4. Log every change
After every transformation that changes shape or content, log it. This is not optional. Default to logging module (saved to file), print allowed when necessary.

### 5. No loops — use maps
Everything is a data transformation. Functionalize the body and map.
- Python: dict/list comprehension or `map()`
- R: `purrr::map()` / `pmap()`

### 6. Comment sections within chains
Use `#` comments to label logical sections (Outcomes, Time variables, etc.)

### 7. Default to pandas — know when to migrate
Start with pandas. Migrate to dask when:
- **RAM**: dataset exceeds ~50% of system memory
- **Time**: a single script takes >5 minutes

### 8. Use accessors when pandas doesn't have a native method
Registered via `pd.api.extensions.register_dataframe_accessor`. Only for operations that would otherwise break pipeline mode (e.g., `.log()`, `.val()`). Never monkey patch. Never wrap things that already exist natively.
- Accessor name: `px` (short for pipe extensions)
- `df.px.log('msg')` — log shape
- `df.px.val(condition, 'msg')` — inline validation

### 9. Write to parquet
Prefer parquet over CSV for all intermediate and output data.

### Preamble (non-package projects)
`src/project/preamble.py` with common imports. Scripts do `from project.preamble import *`. This wildcard is the one exception to the no-wildcard rule.

### R-Specific Additions
- Both `%>%` and `|>` allowed; prefer `%>%` for `.` placeholder
- Always end chains with `identity()`
- Use `<-` for assignment
- `library(tidyverse)` OK in scripts (not in packages)

---

## 7. Enforcement Hierarchy

| Layer | What it catches | When | Hard/Soft |
|---|---|---|---|
| **Linter** (ruff/lintr) | Syntax, naming, imports, security, complexity, builtins, simplification | On save / `make lint` | Hard |
| **Formatter** (ruff format/styler) | Spacing, quotes, line length | On save / `make format` | Hard |
| **Pre-commit hooks** (standard) | Trailing whitespace, large files, merge conflicts, private keys, branch protection | On commit | Hard |
| **Claude review hook** | "What" comments, pipeline style, functions in wrong place, loops over data, hardcoded paths, defensive coding excess, all style guide rules | On commit | Hard |
| **CLAUDE.md** | General project context for Claude | Always | Soft (guidance) |

The goal: everything that can be expressed as a linter rule IS a linter rule. Everything that can't is enforced by a Claude hook. CLAUDE.md is the weakest layer — a suggestion, not a guardrail.

---

## 8. Testing & Correctness

### Pipeline/Data Projects
- **Unit tests**: for all extracted functions in `src/`
- **Integration tests**: verify output schemas (columns exist, shape > 0)
- **Data validation**: built into pipeline chains via `df.px.val(condition, msg)` — same pattern as logging
- **No test stubs auto-generated**: tests written when there's something to test

### Library/Package Projects
- **Every public function has a test**
- **Test stubs auto-generated** alongside modules
- **Python**: pytest in `correctness/tests/`
- **R**: testthat in `correctness/tests/testthat/`

### CI (GitHub Actions)
- `make check` runs lint + test on every push/PR
- Library projects get a `release.yml` workflow
- Regulated projects get a `scheduled-audit.yml`

---

## 9. Files Created (184 total)

### Framework Engine (12 files)
- `init.sh` — interactive wizard entry point
- `TENETS.md` — the five tenets document
- `lib/forest.sh` — prompt primitives (select, confirm, input)
- `lib/resolver.sh` — selections → active modules
- `lib/composer.sh` — file copy + merge strategies
- `lib/templating.sh` — `{{VAR}}` substitution
- `lib/validators.sh` — input validation
- `trees/01_project_type.sh` through `trees/05_data_sensitivity.sh`

### Modules (28 modules, 172 files)
| Category | Modules |
|---|---|
| Always | `_always` (21 template files) |
| Language | `lang_python`, `lang_python_uv`, `lang_python_conda`, `lang_r`, `lang_r_renv` |
| Project Type | `type_dataset_oneoff`, `type_dataset_pipeline_batch`, `type_dataset_pipeline_streaming`, `type_model_classical`, `type_model_ml`, `type_model_llm_app`, `type_model_optimization`, `type_service_api`, `type_service_web`, `type_service_fullstack`, `type_service_cli`, `type_library` |
| Infrastructure | `infra_local`, `infra_cloud_aws`, `infra_cloud_gcp`, `infra_cloud_azure`, `infra_hpc` |
| Team | `team_solo`, `team_collab` |
| Security | `sec_public`, `sec_internal`, `sec_regulated` |

---

## 10. What's Been Tested

| Test | Result |
|---|---|
| Python + uv + batch pipeline + ML + solo + internal | 45 files, 8 modules |
| R + renv + classical stats + team + regulated | 43 files, 7 modules |
| `make help` (both projects) | All targets display correctly |
| Template substitution | All `{{project_name}}` etc. resolved |
| Merge strategy (.gitignore, Makefile, .pre-commit, CLAUDE.md) | Sections append correctly |
| Lock file replay (`--config`) | Identical output |
| Bash syntax check (all scripts + manifests) | All pass |

---

## 11. Topics Not Yet Deep-Dived

- Claude skills and CLAUDE.md content specifics
- Observability config details (logging.yml, monitoring.yml)
- Docker best practices (multi-stage builds, layer caching)
- CI workflow details (caching, matrix builds, deployment)
- DVC / MLflow configuration specifics
- Refactoring schedule and process
- Branch management strategy details
- Chaos engineering approach
- Contract testing specifics
- Automatic test generation

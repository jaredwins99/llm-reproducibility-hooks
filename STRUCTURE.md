# Repository Structure — dev_template proper vs spawned subprojects

This repo holds two kinds of things, and the distinction matters everywhere:

- **dev_template proper** — the product: the `template/` scaffolding system and its shared `reference/` pool, plus repo-level docs and Claude tooling.
- **Spawned subprojects** — independent empirical proofs of concept that were spawned from dev_template and live here for convenience, but stand on their own: `eval/` (the Stan reference-forcing study) and `lexis/` (the lexis/register study). Each can be lifted out of this repo without breaking dev_template proper.

```
dev_template/
├── template/     ← dev_template proper: scaffolding system (creates new projects)
├── reference/    ← dev_template proper: shared pool of scraped ground-truth material
├── eval/         ← subproject: Stan reference-forcing study (independent; PAUSED)
├── lexis/        ← subproject: lexis/register study (independent; ACTIVE)
└── docs/         ← meta: cross-cutting patterns (RATIONALIZATION_PATTERN.md)
```

## dev_template proper — `template/`

The project scaffolding system. A wizard + module composer that creates new opinionated projects.

```
template/
├── init.sh          ← entry point — run to scaffold a new project
├── apply.sh         ← install one module into an existing project, no wizard
├── trees/           ← the 5 interactive decision trees
├── lib/             ← wizard, resolver, composer, templating engines
└── modules/         ← 33 modules with manifests, template files, activation conditions
```

**Usage**: `./template/init.sh --output-dir ~/projects/new-project`

**Existing project**: `./template/apply.sh --module repro_stack --output-dir ~/projects/existing [--claude-private] [--keep-existing]` installs one module without the wizard. `repro_stack` (also offered by the wizard as "Reproducible stack") adds pinned `environment.yml` and `renv.lock`, CmdStan, a Dockerfile, `repro.mk` + `project.mk` make targets (`make setup && make all`, `make check`), pre-commit hooks, `PRINCIPLES.md`, and Claude rules and hooks.

**Decision notes** (wizard question in the Infrastructure tree, default yes; or `apply.sh --module docs_notes`): `docs_notes` adds `notes/` with the four kinds, a checker (`correctness/checks/check_notes.py`) and two git hooks. A note declares the files it covers; `notes/INDEX.md` is generated from those declarations. Four failures gate: a covered file that no longer exists, a source file no note covers, one file decided by two notes, and a finding whose evidence command no longer prints its claim. What must be covered is declared in `notes/coverage.ini` — directories, file kinds, exclusions, and any registry that already documents a module — rather than hardcoded in the checker, since a scope fixed to one language and two directories is how code slips outside the check.

**Optional tools** (wizard questions in the Infrastructure tree, default no; or `apply.sh --module tool_mlflow` / `--module tool_dvc`): `tool_mlflow` adds a local MLflow tracking store in `mlruns/`, a `tracked_run` helper that tags runs with the git commit and pinned-file hashes, and `make mlflow-ui` / `make mlflow-server`. `tool_dvc` adds `dvc.yaml` whose stages call make for each entry of the pipeline order in `project.mk`, `make dvc-*` targets including `dvc-check`, a `DVC_REMOTE` placeholder, and gitignore entries. Both add their package to the conda environment when one exists, so the repro_stack Docker image includes it.

Note: `style_pipelines` activates implicitly (no wizard question) whenever the project types include a dataset flavor (`dataset_oneoff`, `dataset_pipeline_batch`, `dataset_pipeline_streaming`); it is also installable via `apply.sh`.

Template work is under active development on the `hens` branch.

## dev_template proper — `reference/`

Scraped, organized ground-truth source material. Not duplicated per project — projects point at this pool.

```
reference/
└── stan/            ← Stan docs (172 files) + example models (561 .stan files)
    ├── search.sh    ← class-prioritized two-stage search
    ├── INDEX.md     ← full inventory
    └── ...          ← users-guide, reference-manual, example-models, case-studies, forum
```

**Why a shared pool**: reference libraries are large (26MB for Stan alone). Copying them into every scaffolded project is wasteful. Instead, scaffolded projects reference this pool by path or pointer. Future domains (`reference/pandas/`, `reference/numpy/`) will live here too.

**Who uses the pool**:
- The template's `stan.md` rule tells Claude to search `reference/stan/` when editing `.stan` files
- The template's `.stan`-triggered hook runs `reference/stan/search.sh` automatically
- The Stan subproject's eval harness uses the pool as the *independent variable*: "with refs" = pool accessible, "without refs" = pool hidden

**Known gap**: the template's rules and hooks expect `reference/stan/` at the project root, but nothing copies or links the pool into a scaffolded project — outside this repo the hook does nothing. Logged in `ongoing_issues.md` (template-to-pool coupling).

## Subproject — `eval/` (Stan reference-forcing study) — PAUSED

Measurement infrastructure. Runs A/B trials comparing Claude agents with and without access to the reference pool. Spawned from dev_template as its first proof of concept, but independent of it — the harness, tasks, and scorers do not depend on `template/`.

```
eval/
├── harness/         ← the test runner (Python, CLI-based invocation of Claude)
├── tasks/           ← task specs (INGARCH, GP mixture, cross-domain)
├── scoring/         ← objective scorers (compiles? recovers params? PPC quality?)
├── results/         ← JSONL output per trial (gitignored)
└── stan/            ← one-off Stan A/B tests from early experiments (gitignored)
```

**Usage**: `python eval/harness/run.py --task ingarch --model opus --variant with-refs --n 10`

**Status**: paused. Pilot 1 is written up in `eval/RESULTS.md`; the big run `v2run2` stopped at 124/312 trials and its partial JSONL is preserved in `eval/results/` for future resumption. See `ongoing_issues.md` for open design issues.

## Subproject — `lexis/` (lexis/register study) — ACTIVE

Measures how making an LLM inhabit a lexis (a bounded linguistic repertoire) shifts its substantive answers versus the same demand in plain language. Spawned from dev_template (reuses the eval harness pattern) but independent of it. See `lexis/ARCHITECTURE.md`.

```
lexis/
├── harness/         ← 5-agent pipeline (A topic, B role, C lexis, D translator, E respondent)
├── prompts/         ← v1 stage templates
├── v2/              ← v2 config dir: prompts with pinned truth conditions, drift gate, banks, results
├── topics/ roles/   ← v1 vetted banks
└── RESULTS_pilot1.md
```

**Status**: active. Pilot 1 (v1) is written up in `RESULTS_pilot1.md`; pilot 2 (v2, drift-gated) results live in `lexis/v2/results/`.

## How the pieces connect

The template's Stan rule/hook and the Stan subproject both read `reference/`, for different purposes: the template treats it as material scaffolded projects should consult; the eval treats access to it as the experimental manipulation. The subprojects and dev_template proper are otherwise independent — you can use any of them without the others.

## Top-level docs

| File | What | Belongs to |
|---|---|---|
| `STRUCTURE.md` | This file | meta |
| `TENETS.md` | The 5 tenets that organize scaffolded projects | dev_template proper |
| `DECISIONS.md` | Design decisions for the template | dev_template proper |
| `NEXT_STEPS.md` | Current focus + backlog | all |
| `ongoing_issues.md` | Open design questions for the Stan subproject + eval harness | subproject: eval |
| `FELLOWSHIP_PITCH.md` | Fellowship application framing (gitignored) | subprojects |
| `docs/RATIONALIZATION_PATTERN.md` | Reusable doc pattern for rules that fail via self-persuasion | meta |
| `CLAUDE.md` | Always-loaded guidance for Claude sessions | meta |

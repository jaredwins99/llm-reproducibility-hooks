# Repository Structure — Three Layers

This repo is organized into three independent layers. Each has a clear boundary; they connect through the shared reference pool.

```
dev_template/
├── template/     ← Part A: scaffolding system (creates new projects)
├── reference/    ← Shared pool: scraped ground-truth source material
└── eval/         ← Part B: measurement infrastructure (the proof of concept)
```

## Part A — `template/`

The project scaffolding system. A wizard + module composer that creates new opinionated projects.

```
template/
├── init.sh          ← entry point — run to scaffold a new project
├── lib/             ← wizard, resolver, composer, templating engines
└── modules/         ← 28 modules with manifests, template files, activation conditions
```

**Usage**: `./template/init.sh --output-dir ~/projects/new-project`

Part A is mostly complete. It will be revisited after the Stan proof of concept lands.

## Shared Pool — `reference/`

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
- Part A's `stan.md` rule tells Claude to search `reference/stan/` when editing `.stan` files
- Part A's `.stan`-triggered hook runs `reference/stan/search.sh` automatically
- Part B's eval harness uses the pool as the *independent variable*: "with refs" = pool accessible, "without refs" = pool hidden

## Part B — `eval/`

Measurement infrastructure. Runs A/B trials comparing Claude agents with and without access to the reference pool. This is the fellowship proof of concept.

```
eval/
├── harness/         ← the test runner (Python, CLI-based invocation of Claude)
├── tasks/           ← task specs (INGARCH, GP mixture, cross-domain)
├── scoring/         ← objective scorers (compiles? recovers params? PPC quality?)
├── results/         ← JSONL output per trial (gitignored)
└── stan/            ← one-off Stan A/B tests from early experiments (gitignored)
```

**Usage**: `python eval/harness/run.py --task ingarch --model opus --variant with-refs --n 10`

Part B is in active development. See `NEXT_STEPS.md` and `FELLOWSHIP_PITCH.md`.

## How the layers connect

```
┌─────────────┐     copies paths into     ┌─────────────┐
│  template/  │ ────────────────────────→ │  reference/ │
│  (Part A)   │     scaffolded projects   │  (pool)     │
└─────────────┘                            └─────────────┘
                                                  ▲
                                                  │ reads (with-refs variant)
                                                  │ doesn't read (without-refs variant)
                                                  │
                                           ┌──────┴──────┐
                                           │    eval/    │
                                           │  (Part B)   │
                                           └─────────────┘
```

Part A and Part B are independent — you can use either without the other. They share `reference/` because both need verified ground-truth source material, but for different purposes.

## Top-level docs

| File | What | Which layer |
|---|---|---|
| `STRUCTURE.md` | This file | meta |
| `TENETS.md` | The 5 tenets that organize scaffolded projects | Part A |
| `DECISIONS.md` | Design decisions for the template | Part A |
| `NEXT_STEPS.md` | Current focus + backlog | all |
| `FELLOWSHIP_PITCH.md` | Fellowship application framing (gitignored) | Part B |
| `CLAUDE.md` | Always-loaded guidance for Claude sessions | meta |

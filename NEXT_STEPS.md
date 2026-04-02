# Next Steps

## Three Directions

### Direction 1: Test Stan Reference Forcing
- Write a real Stan model and see if the hook + search actually makes Claude reference the docs
- Test with: hierarchical model, mixture model, GP, ODE — each should trigger different reference lookups
- Measure: does Claude get reparameterization right? Does it avoid common mistakes?
- If it works well, this becomes the pattern for all reference libraries

### Direction 2: Scrape Pandas Internals (same pattern as Stan)
- Scrape the pandas docs — especially the hard internals:
  - ExtensionArray API, custom dtypes
  - GroupBy internals (split-apply-combine implementation)
  - Indexing internals (MultiIndex, IntervalIndex)
  - Performance: when copies happen, view vs copy semantics (CoW in pandas 3.0)
  - merge/join algorithms (hash join vs sort merge)
  - eval/query engine
  - Sparse data, categorical internals
  - pipe() and accessor extension mechanisms
- Build same class-prioritized search script
- Hook it to fire on `.py` files that import pandas
- Could extend to: numpy, polars, dask, scikit-learn

### Direction 3: Remaining Deep Dives
Topics not yet configured with specific preferences:

1. **CI workflow details** — GitHub Actions caching, matrix builds (Python + R versions), coverage reporting, deployment steps. Current `ci.yml` is a skeleton that just runs `make check`.

2. **Observability config** — `logging.yml` and `monitoring.yml` are placeholders. Need to decide: log format (JSON vs plain), log levels per environment, what gets logged in data pipelines vs services, retention, rotation. We keep saying "log everything" but haven't wired up how.

3. **Docker best practices** — Current Dockerfiles are basic. Need to discuss: multi-stage builds, layer caching strategy, security scanning (Trivy/Snyk), base image policy (slim vs alpine vs full), .dockerignore optimization.

4. **Branch management** — `conventions.md` has a TODO. Need to decide: trunk-based vs gitflow vs GitHub flow, branch naming, merge strategy (squash vs merge commit), release tagging.

5. **Contract testing** — Mentioned in the plan, `correctness/contracts/` exists but empty. Need to decide: what contracts look like for data pipelines (schema contracts between steps), for APIs (OpenAPI/pact), for ML models (input/output shape contracts).

6. **Chaos engineering** — Mentioned in original scope. Need to decide: is this relevant for data projects? What does chaos look like for pipelines (inject bad data, kill mid-run, corrupt parquet)?

7. **Automatic test generation** — Mentioned in plan. Options: hypothesis (property-based testing), Claude-generated tests via hook, snapshot testing for pipeline outputs.

8. **Refactoring schedule** — `legibility/refactoring.md` is a template. Need to decide: how often, what triggers it (commit count? code complexity threshold?), what the process looks like.

9. **R-specific: lintr decisions doc** — Python has `LINTING_DECISIONS.md` with full audit trail. R doesn't have an equivalent yet.

10. **MCP server configuration** — We said "everything" for Claude features but haven't configured any MCP servers. GitHub MCP for PR context? Slack for notifications?

---

## Current State Summary

### Framework Stats
- **184+ template files** across 28 modules
- **172 Stan reference files** (1.6MB) with class-prioritized search
- **10 commits** on `jaredwins99/dev-template` (private, deploy key configured)
- **Tested**: Python+uv, R+renv, lock file replay — all pass

### What's Built and Configured
- 5 decision trees (all interactive)
- 28 modules with manifests and template files
- Python ruff config: 17 rule categories, single quotes, 88 line length, library-conditional extras (TCH, ANN, D)
- R lintr config: 12 linters, same-line braces, both pipes allowed, tidyverse preferred
- Data pipeline style guide: 9 rules, px accessor, preamble
- Claude tooling: hooks (PreToolUse, PostToolUse, UserPromptSubmit), 3 skills (/review, /pipeline, /refactor), 2 subagents (reviewer, data-pipeline), agent teams (opt-in), commit-counter audit
- Stan reference: 172 files, 3-class search, auto-hook on .stan files
- Orchestration: Makefile always, DVC for Python data, targets for R, Prefect documented
- VS Code nesting: 5 visual groups (.gitignore, reproducibility, correctness, legibility, scripts)
- Post-scaffold: git + GitHub (deploy keys, branch protection), Docker, DVC, MLflow, pre-commit

### Key Design Decisions
- **5 tenets**: Reproducibility, Correctness, Legibility, Observability, Security
- **Library/pipeline split**: libraries are strict, everything else is lean
- **Enforcement hierarchy**: linter (hard) → hooks (hard) → Claude rules (hard) → CLAUDE.md (soft)
- **Comments**: extremely sparse, no "what" comments, em-dash separators
- **Data philosophy**: chains not variables, bare pipeline at script level, no loops, log every change, default pandas, parquet always
- **Commit-based audits**: every N commits, not time-based

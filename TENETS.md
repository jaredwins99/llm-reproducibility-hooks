# The Five Tenets

This framework is organized around exactly five tenets. Every file, folder, and decision maps to one of these five. Five tenets match five decision trees — kept equal for memorability and manageability.

---

## 1. Reproducibility

> If I can't rebuild it from scratch, it doesn't exist.

Everything needed to recreate the environment, data, and outputs from zero. This means:

- **Environment**: Docker containers + language-specific managers (uv/conda for Python, renv/rig for R)
- **Code**: Git version control with clean history
- **Data**: DVC or numerical versioning — every dataset has a version, no ambiguous "raw" vs "processed"
- **Models**: MLflow tracking + model registries for artifact versioning

**Folder**: `reproducibility/`
**Root files nested here (via VS Code)**: `pyproject.toml`, `uv.lock`, `.python-version`, `DESCRIPTION`, `renv.lock`, `Dockerfile`, `docker-compose.yml`

---

## 2. Correctness

> Trust the process, not the person.

Automated gates that prevent bad code from reaching production. No human discipline required — the system enforces quality:

- **Hooks**: Pre-commit hooks that run before every commit
- **CI**: GitHub Actions pipelines that gate every merge
- **Testing**: Test pyramids (unit → integration → contract), automatic test generation
- **Review**: Claude-as-reviewer applying project-specific rules

**Folder**: `correctness/`
**Root files nested here (via VS Code)**: `.pre-commit-config.yaml`

---

## 3. Legibility

> Code is read 10x more than it's written. Optimize for the reader.

Everything that makes the project understandable to a new person (or your future self):

- **Style**: Linter and formatter configs that enforce consistent code style
- **Conventions**: Commit message format, branching strategy, PR process
- **Documentation**: Architecture docs, ADRs, onboarding guide, style guide
- **Tooling**: Claude configuration (CLAUDE.md, skills), IDE settings, Makefile as universal entry point
- **Refactoring**: Scheduled refactoring guidelines to prevent debt accumulation

**Folder**: `legibility/`
**Root files nested here (via VS Code)**: `ruff.toml`, `.lintr`, `CLAUDE.md`, `.claude/`, `.vscode/`, `README.md`, `Makefile`

---

## 4. Observability

> If it ran but nobody saw the logs, did it really run?

Distinguished from legibility: legibility is about making the *process* understandable. Observability is about making the *output* visible:

- **Logging**: Structured logging for applications and data pipelines
- **Monitoring**: Health checks, model performance tracking, data quality metrics
- **Auditing**: Change logs after every meaningful operation
- **Runbooks**: Operational procedures for when things go wrong

**Folder**: `observability/`

---

## 5. Security

> The default must be safe. Unsafe requires explicit opt-in.

Protection of code, data, credentials, and access:

- **Secrets**: `.secrets/` directory (git-ignored), `.env.example` templates (never real values)
- **Ignore files**: Comprehensive `.gitignore`, `.dockerignore`, `.gitattributes`
- **Permissions**: Deploy keys, branch protection rules, CODEOWNERS
- **Scanning**: Dependency vulnerability scanning, scheduled audits
- **Data sensitivity**: Telemetry controls, AI tooling controls, PII handling rules

**Folder**: `security/`
**Root files nested here (via VS Code)**: `.gitignore`, `.gitattributes`, `.dockerignore`, `.github/`

---

## The Five Trees

The five decision trees asked during `init.sh` match the five tenets in number (not in mapping — they're orthogonal axes):

1. **Project Type** (multi-select): What does this project produce?
2. **Language** (multi-select): What languages are used?
3. **Infrastructure** (multi-select): Where does this run?
4. **Team Topology** (single-select): Who works on this?
5. **Data Sensitivity** (multi-select): How sensitive is the data?

Each combination of answers activates a set of modules that populate the five tenet folders with the right files.

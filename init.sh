#!/usr/bin/env bash
# init.sh — Main entry point for The Forest framework
# Walks five decision trees, resolves modules, and composes the project scaffold.

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FOREST_VERSION="0.1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Defaults for CLI flags
# ---------------------------------------------------------------------------
OUTPUT_DIR="."
CONFIG_FILE=""
FORCE=false
NON_INTERACTIVE=false

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    cat <<USAGE
Usage: init.sh [OPTIONS]

Options:
  --output-dir <dir>   Directory to scaffold into (default: current dir)
  --config <lockfile>   Replay from a .dev_template.lock file (non-interactive)
  --force              Overwrite existing project files
  --non-interactive    Accept all defaults without prompting
  -h, --help           Show this help message
  -v, --version        Show version

Examples:
  ./init.sh
  ./init.sh --output-dir ~/projects/my-app
  ./init.sh --config .dev_template.lock --output-dir ~/projects/my-app
USAGE
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --output-dir)
                OUTPUT_DIR="${2:?'--output-dir requires a value'}"
                shift 2
                ;;
            --config)
                CONFIG_FILE="${2:?'--config requires a value'}"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --non-interactive)
                NON_INTERACTIVE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -v|--version)
                echo "The Forest v${FOREST_VERSION}"
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage >&2
                exit 1
                ;;
        esac
    done

    # Resolve to absolute path
    mkdir -p "$OUTPUT_DIR"
    OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
}

# ---------------------------------------------------------------------------
# Source all library files
# ---------------------------------------------------------------------------
load_libs() {
    for lib in "$SCRIPT_DIR"/lib/*.sh; do
        # shellcheck disable=SC1090
        source "$lib"
    done
}

# ---------------------------------------------------------------------------
# Load selections from a lock file (--config mode)
# ---------------------------------------------------------------------------
load_config() {
    local lock_file="$1"

    if [[ ! -f "$lock_file" ]]; then
        echo "ERROR: Config file not found: $lock_file" >&2
        exit 1
    fi

    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// /}" ]] && continue

        if [[ "$line" == *"="* ]]; then
            local key="${line%%=*}"
            local value="${line#*=}"
            SELECTIONS["$key"]="$value"
        fi
    done < "$lock_file"

    echo "Loaded ${#SELECTIONS[@]} selections from $lock_file"
}

# ---------------------------------------------------------------------------
# Collect project metadata (name, description, author)
# ---------------------------------------------------------------------------
ask_metadata() {
    forest_header "Project Metadata"

    local name
    while true; do
        name=$(forest_input "Project name (lowercase, hyphens ok)" "")
        if validate_project_name "$name"; then
            break
        fi
    done
    SELECTIONS[project_name]="$name"

    SELECTIONS[project_description]=$(forest_input "Short description" "")
    SELECTIONS[author_name]=$(forest_input "Author (name or org)" "$(git config user.name 2>/dev/null || echo '')")
}

# ---------------------------------------------------------------------------
# Walk all five decision trees
# ---------------------------------------------------------------------------
walk_trees() {
    local -a tree_files=(
        "$SCRIPT_DIR/trees/01_project_type.sh"
        "$SCRIPT_DIR/trees/02_language.sh"
        "$SCRIPT_DIR/trees/03_infrastructure.sh"
        "$SCRIPT_DIR/trees/04_team_topology.sh"
        "$SCRIPT_DIR/trees/05_data_sensitivity.sh"
    )

    for tree_file in "${tree_files[@]}"; do
        if [[ ! -f "$tree_file" ]]; then
            echo "WARNING: Tree file not found: $tree_file" >&2
            continue
        fi
        # shellcheck disable=SC1090
        source "$tree_file"
    done

    # Call each tree's walk function
    declare -a tree_funcs=(
        tree_01_walk
        tree_02_walk
        tree_03_walk
        tree_04_walk
        tree_05_walk
    )

    for func in "${tree_funcs[@]}"; do
        if declare -F "$func" &>/dev/null; then
            "$func"
        else
            echo "WARNING: Function $func not defined, skipping." >&2
        fi
    done
}

# ---------------------------------------------------------------------------
# Show summary and ask for confirmation
# ---------------------------------------------------------------------------
confirm_selections() {
    forest_summary

    if ! forest_confirm "Proceed with these selections?"; then
        echo "Aborted." >&2
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Post-scaffold setup — interactive dev-environment bootstrapping
# ---------------------------------------------------------------------------
post_scaffold() {
    local project_dir="$1"

    forest_header "Post-Scaffold Setup"

    post_scaffold_git "$project_dir"
    post_scaffold_github "$project_dir"
    post_scaffold_docker_registry "$project_dir"
    post_scaffold_dvc "$project_dir"
    post_scaffold_mlflow "$project_dir"
    post_scaffold_precommit "$project_dir"
}

# -- Git init ---------------------------------------------------------------
post_scaffold_git() {
    local project_dir="$1"

    if [[ -d "$project_dir/.git" ]]; then
        echo "  Git repository already initialised."
        return 0
    fi

    if forest_confirm "Initialise a git repository?"; then
        (
            cd "$project_dir"
            git init -b main
            git add -A
            git commit -m "Initial scaffold from The Forest v${FOREST_VERSION}"
        )
        echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} Git repository initialised with initial commit."
    fi
}

# -- GitHub remote + optional deploy key + branch protection ----------------
post_scaffold_github() {
    local project_dir="$1"

    if ! command -v gh &>/dev/null; then
        echo "  Skipping GitHub setup (gh CLI not found)."
        return 0
    fi

    if ! gh auth status &>/dev/null 2>&1; then
        echo "  Skipping GitHub setup (gh not authenticated)."
        return 0
    fi

    if ! forest_confirm "Create a GitHub remote repository?" "n"; then
        return 0
    fi

    local visibility
    visibility=$(forest_select_one "Repository visibility" \
        "private:Private" \
        "public:Public")

    local repo_name="${SELECTIONS[project_name]}"

    (
        cd "$project_dir"
        gh repo create "$repo_name" --"$visibility" --source=. --push
    )
    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} GitHub repository created and pushed."

    # Deploy key
    _github_deploy_key "$project_dir" "$repo_name"

    # Branch protection
    _github_branch_protection "$repo_name"
}

_github_deploy_key() {
    local project_dir="$1"
    local repo_name="$2"

    if ! forest_confirm "Add a deploy key (read-only SSH key for CI)?" "n"; then
        return 0
    fi

    local key_path="$project_dir/.secrets/deploy_key"
    mkdir -p "$project_dir/.secrets"

    ssh-keygen -t ed25519 -C "deploy-key-${repo_name}" -f "$key_path" -N ""
    gh repo deploy-key add "${key_path}.pub" --repo "$repo_name" --title "forest-deploy-key"

    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} Deploy key generated at .secrets/deploy_key"
    echo "  Private key: $key_path"
    echo "  Add this as a repository secret for CI if needed."
}

_github_branch_protection() {
    local repo_name="$1"

    if ! forest_confirm "Enable branch protection on main?" "n"; then
        return 0
    fi

    local owner
    owner=$(gh api user --jq '.login' 2>/dev/null || true)

    if [[ -z "$owner" ]]; then
        # Try to extract from the remote
        owner=$(gh repo view "$repo_name" --json owner --jq '.owner.login' 2>/dev/null || true)
    fi

    if [[ -z "$owner" ]]; then
        echo "  Could not determine repository owner. Skipping branch protection." >&2
        return 0
    fi

    gh api -X PUT "repos/${owner}/${repo_name}/branches/main/protection" \
        --input - <<'PROTECTION'
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
PROTECTION

    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} Branch protection enabled on main (1 approval required)."
}

# -- Docker registry --------------------------------------------------------
post_scaffold_docker_registry() {
    local project_dir="$1"

    # Only offer if Docker-related modules are active
    if [[ -z "${SELECTIONS[infrastructure]:-}" ]]; then
        return 0
    fi
    if [[ "${SELECTIONS[infrastructure]}" != *"docker"* && "${SELECTIONS[infrastructure]}" != *"kubernetes"* ]]; then
        return 0
    fi

    if ! command -v docker &>/dev/null; then
        echo "  Skipping Docker registry setup (docker not found)."
        return 0
    fi

    if ! forest_confirm "Log in to a Docker registry now?" "n"; then
        return 0
    fi

    local registry
    registry=$(forest_select_one "Which registry?" \
        "ghcr.io:GitHub Container Registry (ghcr.io)" \
        "docker.io:Docker Hub" \
        "custom:Other (enter manually)")

    if [[ "$registry" == "custom" ]]; then
        registry=$(forest_input "Registry URL" "")
    fi

    echo "  Running: docker login $registry"
    docker login "$registry"
    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} Logged in to $registry"
}

# -- DVC --------------------------------------------------------------------
post_scaffold_dvc() {
    local project_dir="$1"

    # Only offer for data-related projects
    if [[ "${SELECTIONS[project_types]:-}" != *"data"* && "${SELECTIONS[project_types]:-}" != *"ml"* ]]; then
        return 0
    fi

    if ! command -v dvc &>/dev/null; then
        echo "  Skipping DVC setup (dvc not found)."
        return 0
    fi

    if ! forest_confirm "Initialise DVC for data versioning?" "n"; then
        return 0
    fi

    (
        cd "$project_dir"
        dvc init
    )
    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} DVC initialised."

    if forest_confirm "Configure a DVC remote now?" "n"; then
        local remote_url
        remote_url=$(forest_input "Remote URL (e.g. s3://bucket/path, gs://bucket/path)" "")
        (
            cd "$project_dir"
            dvc remote add -d storage "$remote_url"
        )
        echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} DVC remote set to $remote_url"
    fi
}

# -- MLflow -----------------------------------------------------------------
post_scaffold_mlflow() {
    local project_dir="$1"

    if [[ "${SELECTIONS[project_types]:-}" != *"ml"* ]]; then
        return 0
    fi

    if ! command -v mlflow &>/dev/null; then
        echo "  Skipping MLflow setup (mlflow not found)."
        return 0
    fi

    if ! forest_confirm "Configure MLflow tracking URI?" "n"; then
        return 0
    fi

    local tracking_uri
    tracking_uri=$(forest_input "MLflow tracking URI" "http://localhost:5000")

    # Write to .env file in the project
    local env_file="$project_dir/.env"
    {
        echo ""
        echo "# MLflow"
        echo "MLFLOW_TRACKING_URI=$tracking_uri"
    } >> "$env_file"

    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} MLflow tracking URI written to .env"
}

# -- Pre-commit -------------------------------------------------------------
post_scaffold_precommit() {
    local project_dir="$1"

    if [[ ! -f "$project_dir/.pre-commit-config.yaml" ]]; then
        return 0
    fi

    if ! command -v pre-commit &>/dev/null; then
        echo "  Skipping pre-commit install (pre-commit not found)."
        return 0
    fi

    if ! forest_confirm "Install pre-commit hooks now?"; then
        return 0
    fi

    (
        cd "$project_dir"
        pre-commit install
    )
    echo -e "  ${FOREST_GREEN}✓${FOREST_RESET} Pre-commit hooks installed."
}

# ---------------------------------------------------------------------------
# Print "next steps" guide
# ---------------------------------------------------------------------------
print_next_steps() {
    local project_dir="$1"

    echo ""
    echo -e "${FOREST_BOLD}${FOREST_GREEN}══════════════════════════════════════${FOREST_RESET}"
    echo -e "${FOREST_BOLD}${FOREST_GREEN}  Your project is ready!${FOREST_RESET}"
    echo -e "${FOREST_BOLD}${FOREST_GREEN}══════════════════════════════════════${FOREST_RESET}"
    echo ""
    echo -e "  ${FOREST_BOLD}Project:${FOREST_RESET}  ${SELECTIONS[project_name]}"
    echo -e "  ${FOREST_BOLD}Location:${FOREST_RESET} $project_dir"
    echo ""
    echo -e "  ${FOREST_BOLD}Next steps:${FOREST_RESET}"
    echo ""
    echo -e "    ${FOREST_CYAN}1.${FOREST_RESET} cd $project_dir"

    if [[ ! -d "$project_dir/.git" ]]; then
        echo -e "    ${FOREST_CYAN}2.${FOREST_RESET} git init && git add -A && git commit -m 'Initial commit'"
    fi

    echo -e "    ${FOREST_CYAN}3.${FOREST_RESET} Read ${FOREST_DIM}CLAUDE.md${FOREST_RESET} for project conventions"
    echo -e "    ${FOREST_CYAN}4.${FOREST_RESET} Run ${FOREST_DIM}make help${FOREST_RESET} to see available targets"

    if [[ "${SELECTIONS[project_types]:-}" == *"data"* || "${SELECTIONS[project_types]:-}" == *"ml"* ]]; then
        echo -e "    ${FOREST_CYAN}5.${FOREST_RESET} Set up data storage with ${FOREST_DIM}dvc remote add${FOREST_RESET}"
    fi

    echo ""
    echo -e "  ${FOREST_DIM}Re-run this scaffold:${FOREST_RESET}"
    echo -e "    init.sh --config $project_dir/.dev_template.lock --output-dir <dir>"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"
    load_libs
    validate_bash_version

    # Global associative array holding every decision
    declare -gA SELECTIONS

    # Check output directory (unless --force)
    if [[ "$FORCE" != true ]]; then
        validate_output_dir "$OUTPUT_DIR"
    fi

    # --config mode: load from lock file and skip interactive prompts
    if [[ -n "$CONFIG_FILE" ]]; then
        load_config "$CONFIG_FILE"
    else
        # Interactive mode
        forest_header "The Forest v${FOREST_VERSION}"
        echo -e "  ${FOREST_DIM}Scaffolding a new project. Answer a few questions and${FOREST_RESET}"
        echo -e "  ${FOREST_DIM}the framework will assemble the right files for you.${FOREST_RESET}"
        echo ""

        ask_metadata
        walk_trees
        confirm_selections
    fi

    # Derive Python-safe package name (hyphens → underscores)
    SELECTIONS[project_name_py]="${SELECTIONS[project_name]//-/_}"

    # Validate we have what we need
    validate_required_selections

    # Resolve which modules to activate
    resolve_modules

    echo ""
    print_active_modules
    echo ""

    # Compose the project
    compose_all "$OUTPUT_DIR"

    # Post-scaffold interactive setup (skip in non-interactive / config mode)
    if [[ "$NON_INTERACTIVE" != true && -z "$CONFIG_FILE" ]]; then
        post_scaffold "$OUTPUT_DIR"
    fi

    print_next_steps "$OUTPUT_DIR"
}

main "$@"

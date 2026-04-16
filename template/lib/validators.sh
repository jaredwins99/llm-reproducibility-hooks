#!/usr/bin/env bash
# validators.sh — Input validation helpers
# Part of The Forest framework

set -euo pipefail

# Validate project name: lowercase, hyphens, underscores, no spaces
validate_project_name() {
    local name="$1"

    if [[ -z "$name" ]]; then
        echo "Project name cannot be empty." >&2
        return 1
    fi

    if [[ ! "$name" =~ ^[a-z][a-z0-9_-]*$ ]]; then
        echo "Project name must start with a lowercase letter and contain only lowercase letters, numbers, hyphens, and underscores." >&2
        return 1
    fi

    if (( ${#name} > 64 )); then
        echo "Project name must be 64 characters or fewer." >&2
        return 1
    fi

    return 0
}

# Validate output directory doesn't already contain a project
validate_output_dir() {
    local dir="$1"

    if [[ -f "$dir/.dev_template.lock" ]]; then
        echo "Directory '$dir' already contains a Forest project (.dev_template.lock found)." >&2
        echo "Use --force to overwrite." >&2
        return 1
    fi

    return 0
}

# Check if a command is available
require_command() {
    local cmd="$1"
    local purpose="${2:-}"

    if ! command -v "$cmd" &>/dev/null; then
        if [[ -n "$purpose" ]]; then
            echo "Required command '$cmd' not found ($purpose)." >&2
        else
            echo "Required command '$cmd' not found." >&2
        fi
        return 1
    fi
    return 0
}

# Check minimum bash version (need 4+ for associative arrays)
validate_bash_version() {
    if (( BASH_VERSINFO[0] < 4 )); then
        echo "ERROR: Bash 4.0+ is required (you have ${BASH_VERSION})." >&2
        echo "On macOS, install with: brew install bash" >&2
        return 1
    fi
    return 0
}

# Validate SELECTIONS has all required keys
validate_required_selections() {
    local -a required=("project_name" "project_types" "languages")

    for key in "${required[@]}"; do
        if [[ -z "${SELECTIONS[$key]:-}" ]]; then
            echo "ERROR: Required selection '$key' is missing." >&2
            return 1
        fi
    done

    return 0
}

#!/usr/bin/env bash
# resolver.sh — Maps SELECTIONS to a list of active modules
# Part of The Forest framework

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$(cd "$SCRIPT_DIR/../modules" && pwd)"

# Evaluate a single activation condition against SELECTIONS
# Conditions:
#   "key=value"    — exact match
#   "key~=value"   — SELECTIONS[key] contains value (comma-separated)
#   "key!=value"   — not equal
# Returns 0 (true) or 1 (false)
eval_condition() {
    local condition="$1"

    if [[ "$condition" == *"~="* ]]; then
        local key="${condition%%~=*}"
        local value="${condition#*~=}"
        local actual="${SELECTIONS[$key]:-}"
        # Check if value appears in comma-separated list
        [[ ",$actual," == *",$value,"* ]]
    elif [[ "$condition" == *"!="* ]]; then
        local key="${condition%%!=*}"
        local value="${condition#*!=}"
        local actual="${SELECTIONS[$key]:-}"
        [[ "$actual" != "$value" ]]
    elif [[ "$condition" == *"="* ]]; then
        local key="${condition%%=*}"
        local value="${condition#*=}"
        local actual="${SELECTIONS[$key]:-}"
        [[ "$actual" == "$value" ]]
    else
        echo "WARNING: Unknown condition format: $condition" >&2
        return 1
    fi
}

# Check if a module should be activated based on its ACTIVATE_WHEN conditions
# Any condition matching (OR logic) activates the module
module_should_activate() {
    local module_dir="$1"
    local manifest="$module_dir/manifest.sh"

    if [[ ! -f "$manifest" ]]; then
        echo "WARNING: No manifest.sh in $module_dir" >&2
        return 1
    fi

    # Source manifest in a subshell to avoid polluting our namespace
    local activate_when
    activate_when=$(
        ACTIVATE_WHEN=()
        # shellcheck disable=SC1090
        source "$manifest"
        printf '%s\n' "${ACTIVATE_WHEN[@]}"
    )

    if [[ -z "$activate_when" ]]; then
        # No conditions means never auto-activate (except _always)
        return 1
    fi

    # OR logic: any matching condition activates
    while IFS= read -r condition; do
        if eval_condition "$condition"; then
            return 0
        fi
    done <<< "$activate_when"

    return 1
}

# Get dependencies for a module
module_dependencies() {
    local module_dir="$1"
    local manifest="$module_dir/manifest.sh"

    if [[ ! -f "$manifest" ]]; then
        return 0
    fi

    (
        DEPENDS_ON=()
        # shellcheck disable=SC1090
        source "$manifest"
        printf '%s\n' "${DEPENDS_ON[@]}"
    )
}

# Get conflicts for a module
module_conflicts() {
    local module_dir="$1"
    local manifest="$module_dir/manifest.sh"

    if [[ ! -f "$manifest" ]]; then
        return 0
    fi

    (
        CONFLICTS_WITH=()
        # shellcheck disable=SC1090
        source "$manifest"
        printf '%s\n' "${CONFLICTS_WITH[@]}"
    )
}

# Global tracking for which modules have been activated (used by _resolve_with_deps)
declare -gA _RESOLVED_MODULES=()

# Main resolver: SELECTIONS → ACTIVE_MODULES array
# Sets global ACTIVE_MODULES as an ordered array of module directory paths
resolve_modules() {
    _RESOLVED_MODULES=()
    ACTIVE_MODULES=()

    # Always include _always first
    ACTIVE_MODULES+=("$MODULES_DIR/_always")
    _RESOLVED_MODULES["_always"]=1

    # Check each module directory
    for module_dir in "$MODULES_DIR"/*/; do
        local module_name
        module_name=$(basename "$module_dir")

        # Skip _always (already added) and hidden dirs
        [[ "$module_name" == "_always" || "$module_name" == .* ]] && continue

        if module_should_activate "$module_dir"; then
            _resolve_with_deps "$module_name"
        fi
    done

    # Check for conflicts
    _check_conflicts
}

# Recursively resolve a module and its dependencies
_resolve_with_deps() {
    local module_name="$1"

    # Skip if already activated
    [[ -n "${_RESOLVED_MODULES[$module_name]:-}" ]] && return 0

    local module_dir="$MODULES_DIR/$module_name"
    if [[ ! -d "$module_dir" ]]; then
        echo "WARNING: Module '$module_name' not found in $MODULES_DIR" >&2
        return 0
    fi

    # Resolve dependencies first
    local deps
    deps=$(module_dependencies "$module_dir")
    while IFS= read -r dep; do
        [[ -z "$dep" ]] && continue
        _resolve_with_deps "$dep"
    done <<< "$deps"

    # Add this module
    _RESOLVED_MODULES[$module_name]=1
    ACTIVE_MODULES+=("$module_dir")
}

# Verify no two active modules conflict
_check_conflicts() {
    local -A active_set=()
    for mod_dir in "${ACTIVE_MODULES[@]}"; do
        active_set[$(basename "$mod_dir")]=1
    done

    for mod_dir in "${ACTIVE_MODULES[@]}"; do
        local mod_name
        mod_name=$(basename "$mod_dir")
        local conflicts
        conflicts=$(module_conflicts "$mod_dir")

        while IFS= read -r conflict; do
            [[ -z "$conflict" ]] && continue
            if [[ -n "${active_set[$conflict]:-}" ]]; then
                echo "ERROR: Module '$mod_name' conflicts with '$conflict'. Both are activated." >&2
                echo "Please adjust your selections to resolve this conflict." >&2
                return 1
            fi
        done <<< "$conflicts"
    done
}

# Print the list of active modules (for debugging/summary)
print_active_modules() {
    echo "Active modules:"
    for mod_dir in "${ACTIVE_MODULES[@]}"; do
        local name
        name=$(basename "$mod_dir")
        local desc=""
        if [[ -f "$mod_dir/manifest.sh" ]]; then
            desc=$(
                MODULE_DESCRIPTION=""
                # shellcheck disable=SC1090
                source "$mod_dir/manifest.sh"
                echo "$MODULE_DESCRIPTION"
            )
        fi
        echo "  - $name: $desc"
    done
}

#!/usr/bin/env bash
# composer.sh — Assembles activated modules into the output directory
# Part of The Forest framework

set -euo pipefail

COMPOSER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$COMPOSER_DIR/templating.sh"

# Merge strategies for accumulator files
# These files can be appended to by multiple modules

# Append lines to a file with a section header comment
# Usage: merge_append <file> <section_name> <content>
merge_append() {
    local file="$1"
    local section="$2"
    local content="$3"

    if [[ ! -f "$file" ]]; then
        echo "$content" > "$file"
        return 0
    fi

    {
        echo ""
        echo "# === $section ==="
        echo "$content"
    } >> "$file"
}

# Merge YAML by appending (for .pre-commit-config.yaml repos list, CI jobs)
# Usage: merge_yaml_append <file> <content>
merge_yaml_append() {
    local file="$1"
    local content="$2"

    if [[ ! -f "$file" ]]; then
        echo "$content" > "$file"
        return 0
    fi

    {
        echo ""
        echo "$content"
    } >> "$file"
}

# Merge Makefile targets by appending
# Usage: merge_makefile <file> <content>
merge_makefile() {
    local file="$1"
    local content="$2"

    if [[ ! -f "$file" ]]; then
        echo "$content" > "$file"
        return 0
    fi

    {
        echo ""
        echo "$content"
    } >> "$file"
}

# Merge JSON by deep-merging objects and concatenating arrays
# Usage: merge_json <file> <content>
merge_json() {
    local file="$1"
    local content="$2"

    if [[ ! -f "$file" ]]; then
        echo "$content" > "$file"
        return 0
    fi

    local script='
import json, sys
def deep_merge(base, incoming):
    if isinstance(base, dict) and isinstance(incoming, dict):
        for key, value in incoming.items():
            base[key] = deep_merge(base[key], value) if key in base else value
        return base
    if isinstance(base, list) and isinstance(incoming, list):
        return base + [item for item in incoming if item not in base]
    return incoming
with open(sys.argv[1]) as handle:
    base = json.load(handle)
incoming = json.loads(sys.stdin.read())
print(json.dumps(deep_merge(base, incoming), indent=2))
'
    local merged
    merged=$(printf '%s' "$content" | python3 -c "$script" "$file")
    echo "$merged" > "$file"
}

# Determine merge strategy for a given file path
# Returns: "append_gitignore", "append_makefile", "append_yaml", "append_generic", "first_wins"
get_merge_strategy() {
    local filepath="$1"
    local basename
    basename=$(basename "$filepath")

    case "$basename" in
        .gitignore|.dockerignore|.gitattributes)
            echo "append_gitignore"
            ;;
        Makefile)
            echo "append_makefile"
            ;;
        .pre-commit-config.yaml|ci.yml)
            echo "append_yaml"
            ;;
        settings.json)
            echo "merge_json"
            ;;
        CLAUDE.md|README.md)
            echo "append_generic"
            ;;
        *)
            echo "first_wins"
            ;;
    esac
}

# Compose a single module's files into the output directory
# Usage: compose_module <module_dir> <output_dir>
compose_module() {
    local module_dir="$1"
    local output_dir="$2"
    local module_name
    module_name=$(basename "$module_dir")
    local files_dir="$module_dir/files"

    if [[ ! -d "$files_dir" ]]; then
        return 0
    fi

    # Process each file in the module
    while IFS= read -r -d '' file; do
        local rel_path="${file#$files_dir/}"

        # Expand template variables in path
        local expanded_path="$rel_path"
        for key in "${!SELECTIONS[@]}"; do
            expanded_path="${expanded_path//\{\{${key}\}\}/${SELECTIONS[$key]}}"
        done

        # Strip .tmpl suffix
        [[ "$expanded_path" == *.tmpl ]] && expanded_path="${expanded_path%.tmpl}"

        local output_path="$output_dir/$expanded_path"
        local strategy
        strategy=$(get_merge_strategy "$expanded_path")

        # Create parent directory
        mkdir -p "$(dirname "$output_path")"

        # Process template if .tmpl, otherwise read as-is
        local content
        if [[ "$file" == *.tmpl ]]; then
            # Process template in memory
            content=$(<"$file")
            for key in "${!SELECTIONS[@]}"; do
                local value="${SELECTIONS[$key]}"
                local escaped_value
                escaped_value=$(printf '%s\n' "$value" | sed 's/[&/\]/\\&/g')
                content=$(echo "$content" | sed "s|{{${key}}}|${escaped_value}|g")
            done
        else
            content=$(<"$file")
        fi

        # Apply merge strategy
        if [[ -f "$output_path" ]]; then
            case "$strategy" in
                append_gitignore)
                    merge_append "$output_path" "$module_name" "$content"
                    ;;
                append_makefile)
                    merge_makefile "$output_path" "$content"
                    ;;
                append_yaml)
                    merge_yaml_append "$output_path" "$content"
                    ;;
                append_generic)
                    merge_append "$output_path" "$module_name" "$content"
                    ;;
                merge_json)
                    merge_json "$output_path" "$content"
                    ;;
                first_wins)
                    # File already exists, skip with notice
                    echo "  SKIP: $expanded_path (already exists, from earlier module)" >&2
                    ;;
            esac
        else
            echo "$content" > "$output_path"
        fi
    done < <(find "$files_dir" -type f -print0)
}

# Add a conda package to the project's environment file(s) unless it is listed.
# Covers repro_stack's environment.yml and lang_python_conda's copy; a later
# `make pin-conda` pins the version. Usage: env_add_conda_package <package>
env_add_conda_package() {
    local package="$1" file added=false
    for file in environment.yml reproducibility/environments/environment.yml; do
        [[ -f "$file" ]] || continue
        added=true
        grep -qE "^[[:space:]]*-[[:space:]]*${package}([=<>! ]|$)" "$file" && continue
        sed -i "0,/^dependencies:/s//dependencies:\n  - ${package}/" "$file"
    done
    if [[ "$added" == false && -f pyproject.toml ]]; then
        echo "  add ${package} to the environment: uv add ${package}"
    fi
}

# Append a line to project.mk (repro_stack) unless it is already there.
# Usage: project_mk_add_line <line>
project_mk_add_line() {
    local line="$1"
    [[ -f project.mk ]] || return 0
    grep -qxF "$line" project.mk || printf '%s\n' "$line" >> project.mk
}

# Run post_install hook for a module if defined
run_post_install() {
    local module_dir="$1"
    local output_dir="$2"
    local manifest="$module_dir/manifest.sh"

    if [[ ! -f "$manifest" ]]; then
        return 0
    fi

    # Check if post_install function exists in manifest
    if grep -q "^post_install()" "$manifest"; then
        (
            cd "$output_dir"
            # shellcheck disable=SC1090
            source "$manifest"
            post_install
        )
    fi
}

# Main composition: process all active modules in order
# Usage: compose_all <output_dir>
# Requires ACTIVE_MODULES array to be set (by resolver.sh)
compose_all() {
    local output_dir="$1"

    echo "Composing project in: $output_dir"
    echo ""

    mkdir -p "$output_dir"

    for module_dir in "${ACTIVE_MODULES[@]}"; do
        local module_name
        module_name=$(basename "$module_dir")
        echo "  Applying module: $module_name"
        compose_module "$module_dir" "$output_dir"
    done

    echo ""
    echo "Running post-install hooks..."

    for module_dir in "${ACTIVE_MODULES[@]}"; do
        run_post_install "$module_dir" "$output_dir"
    done

    # Write the lock file
    _write_lock_file "$output_dir"

    echo ""
    echo "Composition complete."
}

# Write .dev_template.lock with all selections
_write_lock_file() {
    local output_dir="$1"
    local lock_file="$output_dir/.dev_template.lock"

    {
        echo "# Generated by The Forest framework"
        echo "# $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
        echo "#"
        echo "# Re-run with: init.sh --config .dev_template.lock"
        echo ""
        for key in $(echo "${!SELECTIONS[@]}" | tr ' ' '\n' | sort); do
            echo "${key}=${SELECTIONS[$key]}"
        done
        echo ""
        echo "# Active modules:"
        for mod_dir in "${ACTIVE_MODULES[@]}"; do
            echo "# - $(basename "$mod_dir")"
        done
    } > "$lock_file"
}

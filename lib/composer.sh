#!/usr/bin/env bash
# composer.sh — Assembles activated modules into the output directory
# Part of The Forest framework

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/templating.sh"

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

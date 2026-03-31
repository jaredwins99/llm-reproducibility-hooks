#!/usr/bin/env bash
# templating.sh — Lightweight {{VAR}} substitution engine
# Part of The Forest framework

set -euo pipefail

# Process a single template file, replacing {{VAR}} with values from SELECTIONS
# Usage: template_file <input_path> <output_path>
# Reads from SELECTIONS associative array (must be declared in caller)
template_file() {
    local input="$1"
    local output="$2"

    # Start with the input content
    local content
    content=$(<"$input")

    # Replace each {{KEY}} with its value from SELECTIONS
    for key in "${!SELECTIONS[@]}"; do
        local value="${SELECTIONS[$key]}"
        # Escape special sed characters in value
        local escaped_value
        escaped_value=$(printf '%s\n' "$value" | sed 's/[&/\]/\\&/g')
        content=$(echo "$content" | sed "s|{{${key}}}|${escaped_value}|g")
    done

    # Write output, creating parent directories if needed
    mkdir -p "$(dirname "$output")"
    echo "$content" > "$output"
}

# Process all .tmpl files in a directory tree
# Usage: template_directory <input_dir> <output_dir>
# Files ending in .tmpl have the suffix stripped in output
# Template variables in file PATHS are also expanded (e.g., {{project_name}}/)
template_directory() {
    local input_dir="$1"
    local output_dir="$2"

    if [[ ! -d "$input_dir" ]]; then
        return 0
    fi

    # Find all files (not directories) in input
    while IFS= read -r -d '' file; do
        # Compute relative path from input_dir
        local rel_path="${file#$input_dir/}"

        # Expand template variables in the path itself
        local expanded_path="$rel_path"
        for key in "${!SELECTIONS[@]}"; do
            expanded_path="${expanded_path//\{\{${key}\}\}/${SELECTIONS[$key]}}"
        done

        # Strip .tmpl suffix if present
        if [[ "$expanded_path" == *.tmpl ]]; then
            expanded_path="${expanded_path%.tmpl}"
        fi

        local output_path="$output_dir/$expanded_path"

        # If it's a template file, process it; otherwise copy as-is
        if [[ "$file" == *.tmpl ]]; then
            template_file "$file" "$output_path"
        else
            mkdir -p "$(dirname "$output_path")"
            cp "$file" "$output_path"
        fi
    done < <(find "$input_dir" -type f -print0)
}

# Check if a template string contains unresolved variables
# Usage: if template_has_unresolved "$string"; then warn; fi
template_has_unresolved() {
    local content="$1"
    echo "$content" | grep -qE '\{\{[A-Za-z_]+\}\}'
}

# List all unresolved variables in a file
# Usage: template_list_unresolved <file_path>
template_list_unresolved() {
    local file="$1"
    grep -oE '\{\{[A-Za-z_]+\}\}' "$file" | sort -u | sed 's/{{//;s/}}//'
}

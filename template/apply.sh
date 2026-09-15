#!/usr/bin/env bash
# apply.sh — install modules into an existing project without the wizard.
#
#   template/apply.sh --module repro_stack --output-dir ~/projects/hens \
#       [--set key=value ...] [--claude-private] [--keep-existing]
#
# Files that already exist are kept (first-wins), accumulator files
# (.gitignore, .dockerignore, settings.json, CLAUDE.md) are merged, and each
# module's post_install hook runs. Dependencies are not pulled in: an existing
# project already has its own layout.
#
#   --claude-private  gitignore .claude/ and CLAUDE.md (projects whose Claude
#                     material must stay local)
#   --keep-existing   never replace a project's own Dockerfile

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR=""
MODULES=()
SETS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --module) MODULES+=("${2:?}"); shift 2 ;;
        --output-dir) OUTPUT_DIR="${2:?}"; shift 2 ;;
        --set) SETS+=("${2:?}"); shift 2 ;;
        --claude-private) export REPRO_CLAUDE_PRIVATE=1; shift ;;
        --keep-existing) export REPRO_KEEP_EXISTING=1; shift ;;
        -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

[[ -n "$OUTPUT_DIR" && ${#MODULES[@]} -gt 0 ]] || { sed -n '2,17p' "$0" >&2; exit 1; }
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

for lib in "$SCRIPT_DIR"/lib/*.sh; do
    # shellcheck disable=SC1090
    source "$lib"
done

declare -gA SELECTIONS
if [[ -f "$OUTPUT_DIR/.dev_template.lock" ]]; then
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" == \#* ]] && continue
        SELECTIONS["$key"]="$value"
    done < "$OUTPUT_DIR/.dev_template.lock"
fi
SELECTIONS[project_name]="${SELECTIONS[project_name]:-$(basename "$OUTPUT_DIR" | tr '[:upper:] _' '[:lower:]--')}"
SELECTIONS[project_description]="${SELECTIONS[project_description]:-}"
SELECTIONS[author_name]="${SELECTIONS[author_name]:-$(git config user.name 2>/dev/null || true)}"
for kv in "${SETS[@]}"; do
    SELECTIONS["${kv%%=*}"]="${kv#*=}"
done
SELECTIONS[project_name_py]="${SELECTIONS[project_name]//-/_}"

for module in "${MODULES[@]}"; do
    module_dir="$SCRIPT_DIR/modules/$module"
    [[ -d "$module_dir" ]] || { echo "No module named $module" >&2; exit 1; }
    echo "Applying $module to $OUTPUT_DIR"
    compose_module "$module_dir" "$OUTPUT_DIR"
    run_post_install "$module_dir" "$OUTPUT_DIR"
done

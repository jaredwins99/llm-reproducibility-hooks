#!/usr/bin/env bash
# Generate STRUCTURE.md — an ASCII tree of the project for Claude to read
# Called by the commit-counter hook, not on every commit

set -euo pipefail

OUTPUT="STRUCTURE.md"

{
    echo "# Project Structure"
    echo ""
    echo "Auto-generated file tree. Updated every ${AUDIT_INTERVAL:-10} commits."
    echo "Last updated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo ""
    echo '```'
    if command -v tree &>/dev/null; then
        tree -a -I '.git|__pycache__|.pytest_cache|node_modules|.ruff_cache|renv/library|.venv|venv' --dirsfirst -F
    else
        find . -not -path './.git/*' \
               -not -path './__pycache__/*' \
               -not -path './.pytest_cache/*' \
               -not -path './.venv/*' \
               -not -name '*.pyc' \
            | sort \
            | sed 's|^./||' \
            | head -200
    fi
    echo '```'
} > "$OUTPUT"

echo "[structure] Updated $OUTPUT"

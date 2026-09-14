#!/usr/bin/env bash
set -euo pipefail

TARGETS=()
for d in src scripts; do
    [[ -d "$d" ]] && TARGETS+=("$d")
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    exit 0
fi

if ! python correctness/checks/check_pipelines.py "${TARGETS[@]}"; then
    echo ""
    echo "Blocked by the pandas pipeline style gate."
    echo "See legibility/style-pipelines.md for each rule and its rationale."
    exit 1
fi

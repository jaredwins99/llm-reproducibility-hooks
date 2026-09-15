#!/usr/bin/env bash
# PostToolUse hook on Edit|Write: after a Python or R file is edited, run the
# project formatter (make format). Formatting failures never block the edit.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null)
[[ "$file" =~ \.(py|R|r)$ && -f "$file" ]] || exit 0

cd "$root" && make -s format >/dev/null 2>&1
exit 0

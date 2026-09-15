#!/usr/bin/env bash
# PreToolUse hook on Edit|Write: before a .stan file is edited, search the
# Stan reference pool for the constructs it uses and add the matches to
# Claude's context. Never blocks the edit.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null)
[[ "$file" == *.stan && -f "$file" ]] || exit 0

search="$root/reference/stan/search.sh"
[[ -f "$search" ]] || exit 0

matches=$(cd "$root" && bash "$search" --from-file "$file" 2>/dev/null | head -80)
[[ -n "$matches" ]] || exit 0

printf '=== Stan reference search (auto-fired on .stan edit) ===\n%s\n' "$matches" |
    python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": sys.stdin.read()}}))'
exit 0

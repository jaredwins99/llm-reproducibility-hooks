#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a git commit whose command line carries AI or
# co-author attribution, or a message written about a user or an agent.
# The commit-msg hook in .pre-commit-config.yaml enforces the same rule for
# every contributor; this catches it before the command runs.
set -uo pipefail

cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null)
[[ "$cmd" == *"git commit"* ]] || exit 0

if grep -qiE 'co-authored-by:|generated (with|by) .*claude|claude-session:|noreply@anthropic\.com|🤖' <<<"$cmd"; then
    echo "Commit rules: no Co-Authored-By, 'Generated with' or any AI attribution. Remove it and commit again." >&2
    exit 2
fi
if grep -qiE '\b(per (the )?user|(the )?user (asked|requested|wanted|wants)|as requested|as you asked)\b' <<<"$cmd"; then
    echo "Commit rules: the message states what the change does and never refers to a user or an agent." >&2
    exit 2
fi
exit 0

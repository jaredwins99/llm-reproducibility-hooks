#!/usr/bin/env bash
# PostToolUse hook: run the pipe gate on a Python file Claude just wrote.
# Exit 2 returns the violations to Claude, which must fix the code; the gate
# is not to be weakened, silenced with noqa, or dodged by moving the file.
#
# One source for both modules: style_pipelines ships it and repro_stack copies
# it. With repro.mk present the gate and its directories come from make
# (make gate, GATE_DIRS); otherwise the checker runs on src/ and scripts/.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null)
[[ "$file" == *.py && -f "$file" ]] || exit 0

cd "$root" || exit 0
rel="${file#"$root"/}"
if [[ -f repro.mk ]]; then
    dirs=$(make -s print-GATE_DIRS 2>/dev/null)
    gate=(make -s gate GATE_DIRS="$rel")
    guide=PRINCIPLES.md
else
    dirs="src scripts"
    gate=("$(command -v python || command -v python3)" correctness/checks/check_pipelines.py "$rel")
    guide=legibility/style-pipelines.md
fi

inside=false
for d in $dirs; do
    [[ "$rel" == "$d"/* ]] && inside=true
done
$inside || exit 0

if ! out=$("${gate[@]}" 2>&1); then
    printf '%s\n\nBlocked by the pipe gate. Fix the code; see %s.\n' "$out" "$guide" >&2
    exit 2
fi
exit 0

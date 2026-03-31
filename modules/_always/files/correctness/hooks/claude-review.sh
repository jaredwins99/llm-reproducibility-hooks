#!/usr/bin/env bash
# Pre-commit hook: Claude reviews staged changes against all project rules
# Part of the Correctness tenet — hard enforcement, not a suggestion
#
# This hook sends the diff to Claude with the full style guide and linting
# rules as context, and rejects commits that violate them.

set -euo pipefail

# Only run if claude CLI is available
if ! command -v claude &>/dev/null; then
    echo "SKIP: claude CLI not found, skipping Claude review"
    exit 0
fi

# Get the staged diff
diff=$(git diff --cached --unified=3)

if [[ -z "$diff" ]]; then
    exit 0
fi

# Find project style guide and rules
style_guide=""
if [[ -f "legibility/style-guide.md" ]]; then
    style_guide+=$(cat "legibility/style-guide.md")
    style_guide+=$'\n\n'
fi
# Append any language-specific style guides
for sg in legibility/style-guide-*.md; do
    if [[ -f "$sg" ]]; then
        style_guide+=$(cat "$sg")
        style_guide+=$'\n\n'
    fi
done

# Build the review prompt
review_prompt="You are a strict code review hook enforcing project rules. Review the following diff against these rules.

RULES:
${style_guide}

ADDITIONAL RULES:
- Comments must be extremely sparse. Reject 'what' comments that restate the code. Only 'why' comments and pipeline section labels are allowed.
- Section separators must use the em dash format: # ———————————————————————————————————
- All functions belong in src/, never in scripts/. Scripts contain only the pipeline chain and imports.
- No loops over data — use map/comprehensions/groupby instead.
- Log every data transformation step.
- Use OS-portable paths (pathlib in Python, file.path in R). Never hardcode / or \\.

DIFF:
${diff}

If ALL code passes the rules, output exactly: PASS
If any violations are found, output each violation as:
FILE:LINE: [RULE] description of violation

Be strict. Only flag clear violations, not style preferences."

result=$(echo "$review_prompt" | claude --print -p -)

if [[ "$result" == "PASS" ]]; then
    exit 0
fi

echo ""
echo "REJECTED: Claude review found rule violations."
echo ""
echo "$result"
echo ""
exit 1

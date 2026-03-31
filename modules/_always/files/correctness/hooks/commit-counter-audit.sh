#!/usr/bin/env bash
# Post-commit hook: run audits after every N commits
# Trigger-based, not time-based — respects that not everyone wants a cron

set -euo pipefail

AUDIT_INTERVAL="${AUDIT_INTERVAL:-10}"  # default: every 10 commits
COUNTER_FILE=".claude/.commit_count"

# Initialize counter if missing
if [[ ! -f "$COUNTER_FILE" ]]; then
    echo "0" > "$COUNTER_FILE"
fi

# Increment
count=$(cat "$COUNTER_FILE")
count=$((count + 1))
echo "$count" > "$COUNTER_FILE"

if (( count >= AUDIT_INTERVAL )); then
    echo "--- Commit #${count}: running scheduled audit ---"

    # Reset counter
    echo "0" > "$COUNTER_FILE"

    # Update project structure file
    echo "[audit] Updating STRUCTURE.md..."
    bash correctness/hooks/update-structure.sh 2>&1 || true
    git add STRUCTURE.md 2>/dev/null && git commit -m "chore: update STRUCTURE.md" --no-verify 2>/dev/null || true

    # Run lint on full codebase
    echo "[audit] Running full lint..."
    make lint 2>&1 || true

    # Check for outdated dependencies (if tools available)
    if command -v uv &>/dev/null; then
        echo "[audit] Checking Python dependencies..."
        uv pip list --outdated 2>/dev/null || true
    fi

    # Run Claude review on recent changes since last audit
    if command -v claude &>/dev/null; then
        echo "[audit] Running Claude review on recent changes..."
        git log --oneline -"$AUDIT_INTERVAL" | claude --print -p "Review these recent commits for style drift against the project rules. Flag any patterns that are slipping." 2>/dev/null || true
    fi

    echo "--- Audit complete ---"
fi

#!/usr/bin/env python3
"""Stop hook: block turn-end if code edits weren't followed by a real execution.

Policy:
  - If no Edit/Write/NotebookEdit this turn -> allow (exit 0).
  - If all edits were to docs (.md/.mdx/.txt/.rst) -> any Bash after last edit unblocks.
  - If any code file was edited -> require a Bash command after the last edit whose
    string mentions the basename stem of at least one edited code file. This prevents
    `echo foo`-style no-op bypass of the validation rule.

Input: JSON on stdin from Claude Code's Stop event (contains transcript_path).
Exit 0: allow turn to end.
Exit 2: block turn; stderr is shown to Claude as feedback.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

LOG_PATH = "/tmp/stop-hook.log"


def _log(message: str) -> None:
    try:
        with open(LOG_PATH, "a") as f:
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            f.write(f"[{ts}] {message}\n")
    except OSError:
        pass

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
EXEC_TOOLS = {"Bash"}
DOCS_EXTS = {".md", ".mdx", ".txt", ".rst"}


def main() -> int:
    _log("FIRED")
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        _log("  exit 0 (malformed payload)")
        return 0

    transcript_path = payload.get("transcript_path")
    _log(f"  transcript={transcript_path!r}")
    if not transcript_path:
        _log("  exit 0 (no transcript_path)")
        return 0

    try:
        with open(transcript_path) as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        _log("  exit 0 (transcript not found)")
        return 0

    messages = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    # Last REAL user message = start of the current turn.
    # In Claude Code transcripts, type="user" is also used for tool_result messages;
    # those are not turn boundaries. A real user message has text content (or a string).
    def is_real_user(msg: dict) -> bool:
        if msg.get("type") != "user":
            return False
        content = msg.get("message", {}).get("content")
        if isinstance(content, str):
            return True
        if not isinstance(content, list):
            return False
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                return False
        return True

    last_user_idx = None
    for i, msg in enumerate(messages):
        if is_real_user(msg):
            last_user_idx = i
    if last_user_idx is None:
        _log("  exit 0 (no user messages)")
        return 0

    # Collect tool_use events in order after the last user message.
    events: list[tuple[str, dict]] = []
    for msg in messages[last_user_idx + 1 :]:
        if msg.get("type") != "assistant":
            continue
        content = msg.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                name = item.get("name", "")
                inp = item.get("input", {}) or {}
                events.append((name, inp))

    if not events:
        _log("  exit 0 (no tool_use events this turn)")
        return 0

    # Find last edit position and collect edited paths.
    last_edit_pos: int | None = None
    edited_paths: list[str] = []
    for i, (name, inp) in enumerate(events):
        if name in EDIT_TOOLS:
            last_edit_pos = i
            fp = inp.get("file_path", "")
            if fp:
                edited_paths.append(fp)

    if last_edit_pos is None:
        _log("  exit 0 (no edits this turn)")
        return 0

    # Bash commands after the last edit.
    bash_after_commands: list[str] = []
    for i, (name, inp) in enumerate(events):
        if i <= last_edit_pos:
            continue
        if name in EXEC_TOOLS:
            bash_after_commands.append(inp.get("command", ""))

    if not bash_after_commands:
        _log(f"  exit 2 (no bash after edit) edits={edited_paths}")
        print(_block_no_bash_message(edited_paths), file=sys.stderr)
        return 2

    # Classify: docs-only vs has code edits.
    code_paths = [p for p in edited_paths if Path(p).suffix.lower() not in DOCS_EXTS]
    if not code_paths:
        _log(f"  exit 0 (docs-only edits, bash present) edits={edited_paths}")
        return 0

    # Code was edited; require at least one Bash command after to reference an edited file.
    stems = {Path(p).stem for p in code_paths if Path(p).stem}
    # Also allow match on full basename (in case stem collides with something short).
    basenames = {Path(p).name for p in code_paths}
    targets = stems | basenames

    for cmd in bash_after_commands:
        if any(t and t in cmd for t in targets):
            _log(f"  exit 0 (bash references edit) code={code_paths}")
            return 0

    _log(f"  exit 2 (bash did not reference edit) code={code_paths} cmds={bash_after_commands}")
    print(_block_code_bypass_message(code_paths, bash_after_commands), file=sys.stderr)
    return 2


def _block_no_bash_message(edited_paths: list[str]) -> str:
    paths_str = "\n  ".join(edited_paths[:5])
    return (
        "VALIDATION HOOK — turn blocked.\n\n"
        "You edited files this turn but did not run anything after your last edit:\n"
        f"  {paths_str}\n\n"
        "Empirical validation is mandatory before ending a turn. Run the relevant test "
        "or execute the changed code now, then the turn will unblock.\n\n"
        "If ALL your edits this turn were to docs/text files (.md, .mdx, .txt, .rst), "
        "any Bash call will satisfy the hook.\n\n"
        "See .claude/rules/validation.md for the rule this enforces."
    )


def _block_code_bypass_message(code_paths: list[str], bash_cmds: list[str]) -> str:
    paths_str = "\n  ".join(code_paths[:5])
    cmds_str = "\n  ".join(c[:100] for c in bash_cmds[:5])
    return (
        "VALIDATION HOOK — turn blocked.\n\n"
        "You edited code files this turn:\n"
        f"  {paths_str}\n\n"
        "You ran Bash commands after, but none of them reference any of the edited files:\n"
        f"  {cmds_str}\n\n"
        "Code edits require a Bash command that actually exercises the changed code — "
        "running the file, running its tests, or otherwise invoking the filename. "
        "`echo \"acknowledged\"` is NOT sufficient for code changes.\n\n"
        "See .claude/rules/validation.md for the rule this enforces."
    )


if __name__ == "__main__":
    sys.exit(main())

"""Dataclasses and parsing helpers for the lexis pipeline."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Any

STAGES = ("A", "B", "C", "D", "E")
DEFAULT_ARMS = ("lexis", "control")


@dataclass
class StageOutput:
    """One agent invocation: what we sent, what came back."""

    stage: str
    prompt: str
    raw: str
    parsed: dict[str, Any] | None
    wall_s: float
    exit_code: int | None
    status: str  # completed | timeout | crashed

    def brief(self) -> dict[str, Any]:
        """Row-friendly summary (drops the long prompt/raw texts)."""
        return {
            "stage": self.stage,
            "wall_s": self.wall_s,
            "exit_code": self.exit_code,
            "status": self.status,
            "parsed_ok": self.parsed is not None,
        }


def extract_json(text: str) -> dict[str, Any] | None:
    """Extract the last JSON object from agent output.

    Agents are instructed to output a single JSON object; models sometimes wrap
    it in prose or code fences. Scan for balanced top-level {...} blocks and
    return the last one that parses.
    """
    candidates = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    candidates.append(text[start : i + 1])
    for cand in reversed(candidates):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def extract_answer(text: str, allowed: list[str]) -> str | None:
    """Parse the final forced answer from E's output.

    Takes the LAST line matching 'ANSWER: <x>' and returns x if it is one of
    the allowed answers (case-insensitive). None if absent or not allowed —
    recorded as a finding, not an error.
    """
    matches = re.findall(r"ANSWER:\s*([A-Za-z0-9_\-]+)", text)
    if not matches:
        return None
    final = matches[-1].upper()
    allowed_upper = {a.upper() for a in allowed}
    return final if final in allowed_upper else None

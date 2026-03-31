---
description: Defensive coding rules — strictness depends on project type
globs: ["**/*.py", "**/*.R"]
---

# Defensive Coding

## Pipeline and script code (`scripts/`)

Let it crash with clear tracebacks. Failures should be loud and obvious.

- No gratuitous `try`/`except` or `tryCatch`. If something is wrong, the process should die.
- No `isinstance` checks. Data coming from upstream steps has a known shape.
- No `None` guards or null checks unless the data genuinely has optional fields.
- No wrapping simple operations in `try`/`except` just to log and re-raise. The traceback already tells you what happened.

## Library and package code (`src/`)

Validate inputs at public API boundaries. Users of your functions deserve clear error messages.

- Use `try`/`except` (or `tryCatch`) when callers need actionable error messages instead of raw tracebacks.
- Validate types and shapes at the entry point of public functions.
- Internal helper functions can assume valid input — the public boundary already checked.

## General

- Never catch broad exceptions (`except Exception`, `tryCatch(expr, error = ...)`) unless you are at the top-level entry point of a CLI or service.
- Never silence errors. If you catch, either handle meaningfully or let it propagate.

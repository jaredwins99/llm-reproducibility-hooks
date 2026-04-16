---
description: Code style enforcement rules
globs: ["**/*.py", "**/*.R", "**/*.r"]
---

# Style Rules

## Comments

Code speaks for itself. Never write "what" comments that restate the code.
Only write "why" comments when the reason is not obvious from context.

## Section separators

Use em dashes (`# ---`) to separate logical sections. No ASCII art, no banners, no box-drawing characters.

## Project layout

- Functions always live in `src/`. Never define reusable functions in `scripts/`.
- `scripts/` contains pipeline code that calls functions from `src/`.

## Logging

Log every data transformation step. The log line should say what changed and the resulting shape or row count.

## Iteration

No loops over data. Functionalize the operation and map/apply it.
Use `map()` / `lapply()` / `.apply()` / vectorized operations instead of `for` loops over rows or elements.

## Paths

OS-portable paths always. Use `pathlib.Path` in Python and `file.path()` in R.
Never use string concatenation for paths. Never hardcode `/` or `\\`.

## Constants

Constants go in `UPPER_CASE` at the top of each script, below imports.

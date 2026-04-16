---
name: refactor
description: Refactor code following project conventions
---

# Refactor Skill

When the user runs `/refactor`, follow these steps:

## 1. Read the target file

Read the file the user wants refactored. If no file is specified, ask which file to refactor.

## 2. Check against all style rules

Load `legibility/style-guide.md` and any `legibility/style-guide-*.md` files. Audit the target file against every rule.

## 3. Extract repeated code into functions in src/

Identify repeated logic or reusable blocks. Extract them into properly named functions placed in the appropriate module under `src/`. Scripts should only contain pipeline orchestration, never function definitions.

## 4. Ensure all functions are in src/, not scripts/

If any function definitions exist in `scripts/`, move them to the correct module in `src/` and replace them with imports.

## 5. Replace loops with maps/comprehensions

Where a loop iterates to build or transform a collection, replace it with a map, list comprehension, or vectorized operation as appropriate for the language.

## 6. Add logging after data transformation steps

Every step that transforms data should be followed by a logging call that reports what happened (row count, column changes, etc.).

## 7. Ensure OS-portable paths

Replace any hardcoded path separators (`/` or `\`) with `pathlib.Path` or the language's equivalent portable path construction.

## 8. Fix comments

Remove "what" comments that merely restate the code. Keep "why" comments that explain intent or reasoning. Add "why" comments where non-obvious decisions lack explanation.

## 9. Use section separators

Ensure logical sections are separated with em-dash (`---`) comment separators in the project's standard format.

## 10. Show diff and confirm

After preparing all changes, show the user a complete diff of what will change. Ask for explicit confirmation before applying any modifications.

---
name: review
description: Review staged changes against all project style rules
---

# Review Skill

When the user runs `/review`, follow these steps:

## 1. Get staged changes

Run `git diff --cached` to capture all staged changes. If nothing is staged, tell the user and stop.

## 2. Load style rules

Read the style guide from `legibility/style-guide.md`. Also check for any supplemental guides matching `legibility/style-guide-*.md` and load those too. All rules from every loaded guide apply.

## 3. Check every change against all rules

For each changed file and each changed line, verify compliance with every applicable rule:

- **Comments policy** -- No "what" comments that merely restate the code. Only "why" comments that explain intent or reasoning are allowed.
- **Naming** -- All identifiers use `snake_case`. No camelCase, no PascalCase except where the language requires it (e.g., class names in Python).
- **Section separators** -- Sections within a file are separated using em-dash (`---`) comment separators in the project's standard format.
- **Defensive coding** -- Conditional on project type: assert preconditions, validate inputs, fail early with clear messages.
- **Pipeline style** -- If changes touch files in `scripts/`, verify they follow pipeline rules: bare chain style, logging after each step, functions live in `src/` not `scripts/`.
- **Path construction** -- All paths must be OS-portable. Use `pathlib.Path` or equivalent, never hardcoded `/` or `\` separators.

## 4. Report violations

Output each violation in the format:

```
FILE:LINE: [RULE] description
```

Where RULE is one of: COMMENTS, NAMING, SEPARATORS, DEFENSIVE, PIPELINE, PATHS.

## 5. Clean result

If no violations are found, output:

```
All clear
```

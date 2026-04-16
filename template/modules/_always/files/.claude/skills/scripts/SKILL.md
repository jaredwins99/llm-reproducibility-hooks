---
name: pipeline
description: Create a new numbered pipeline script with proper structure
---

# Pipeline Skill

When the user runs `/pipeline`, follow these steps:

## 1. Determine the next script number

Look at existing scripts in `scripts/` and find the highest numbered prefix (e.g., `01_extract.py`, `02_transform.py`). The new script gets the next number, zero-padded to two digits.

## 2. Ask what the step does

Ask the user what this pipeline step does. Common types: extract, transform, load, validate, export, enrich. Use the answer to name the file (e.g., `03_enrich.py`).

## 3. Create the script

Generate the script with the following structure:

- **Preamble import** -- Import the project's shared preamble module at the top.
- **Section separators** -- Use em-dash (`---`) comment separators between logical sections.
- **Bare pipeline chain** -- Write the main logic as a chained pipeline, not as sequential variable reassignments. Each transformation step chains from the previous one.
- **Logging after each step** -- Add a logging call after each transformation step so the pipeline's progress is observable.
- **Parquet output** -- The final output writes to parquet format by default.

## 4. Follow all pipeline style rules

Consult the style guide at `legibility/style-guide.md` and ensure the generated script follows every pipeline rule. Functions belong in `src/`, not in the script itself. The script should only contain the pipeline chain and its orchestration.

# Rule Pattern: Rationalizations + Red Flags + Verification

Inspired by addyosmani/agent-skills. Use this structure when a rule needs *principled* force, not just imperative force — when the reader is likely to invent reasons to skip it.

## Template

```markdown
### Rule: <one-line statement>

**Do**: <concrete example>
**Don't**: <concrete anti-example>

**Rationalizations** (what you'll tell yourself to skip this):
| Excuse | Reality |
|---|---|
| "<plausible-sounding excuse>" | <why it's wrong, ideally with evidence> |
| "<another excuse>" | <counter> |

**Red flags** (signs you've violated this):
- <observable symptom 1>
- <observable symptom 2>

**Verification**:
- [ ] <check 1>
- [ ] <check 2>
```

## Worked example — Pipeline philosophy

### Rule: Pipelines — no try/except, let it crash

**Do**: just read the file, just call the function. If it fails, it fails.
```python
df = pd.read_parquet(path)
df = df.pipe(clean).pipe(transform)
```

**Don't**: wrap things "just in case."
```python
try:
    df = pd.read_parquet(path)
except Exception as e:
    logger.error(f"Failed: {e}")
    raise  # this block does nothing Python doesn't already do
```

**Rationalizations**:
| Excuse | Reality |
|---|---|
| "What if the file is corrupt?" | Python will tell you with a traceback. Better log than anything you'd write. |
| "What if a column is missing?" | Let KeyError surface with the exact column name. Don't pre-check. |
| "I want a nicer error message" | You don't. You want the original traceback so you can find the bug. |
| "Defensive coding is good practice" | In libraries yes (user-facing boundary). In pipelines no — the caller is you. |

**Red flags**:
- Any `try`/`except` block in a script-level pipeline
- Pre-validation (`if not df.empty`, `if "col" in df.columns`) before the operation
- Default values (`.get("col", 0)`) hiding missing data

**Verification**:
- [ ] Zero `try` blocks in pipeline scripts
- [ ] Operations chain directly; errors propagate naturally
- [ ] Validation lives at data ingestion boundary only, not throughout

## When to use this pattern

Apply only when:
- The rule is counter-intuitive or contradicts common-sense defaults
- There's empirical evidence (A/B test, known failure mode, incident)
- The rule is frequently violated by new contributors

Don't apply to obvious rules (e.g., "use type hints in libraries") — the overhead isn't worth it.

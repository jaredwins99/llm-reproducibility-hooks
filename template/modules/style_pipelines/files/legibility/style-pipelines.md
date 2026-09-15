# Pandas pipeline style — {{project_name}}

Every dataframe transformation is a chain, and every step reports what it
changed. Those are gated, not suggested: `correctness/checks/check_pipelines.py`
runs on write, on commit, and in CI, and exits non-zero on violation.

Inline comments are discouraged but not gated. The checker reports them as
advisory findings, and `--strict` turns them into failures for projects that
want that.

Written in the Rationalizations + Red Flags + Verification pattern
(`docs/RATIONALIZATION_PATTERN.md`) because all three rules are ones a
contributor will talk themselves out of.

---

### Rule: transformations chain with `.pipe()` — never reassign a frame from itself

**Do**: one expression, each step a named function.
```python
out = (raw
       .pipe(drop_empty_columns)
       .pipe(flags_to_boolean)
       .pipe(add_timestamp))
```

**Don't**: a ladder of reassignments.
```python
df = pd.read_parquet(path)
df = df.dropna()
df = df.head(10)
```

**Rationalizations**:
| Excuse | Reality |
|---|---|
| "I tried piping it and it didn't work" | You tried once. A step that resists `.pipe()` is almost always a step doing two things; split it and both halves pipe. Attempt count is not evidence. |
| "This step needs two inputs" | `.pipe(fn, other=df2)` passes anything. `.pipe` forwards every extra argument. |
| "I need an intermediate for debugging" | `.pipe(print_shape)` mid-chain, or break the chain temporarily and restore it before commit. Debugging scaffolding is not a style exemption. |
| "It's only two steps" | Two becomes six. The ladder has no natural stopping point; the chain does. |
| "Assignment is more readable" | It reads as six unrelated statements that happen to share a name. The chain reads as one transformation with named stages. |

**Red flags**:
- The same name on both sides of `=` more than once in a scope
- `inplace=True` anywhere
- `df["col"] = ...` instead of `.assign(col=...)`
- An intermediate name used exactly once

**Verification**:
- [ ] `check_pipelines.py` reports no PIPE002 or PIPE003
- [ ] Every transformation function takes a frame and returns a frame
- [ ] No `inplace=True` in the codebase

---

### Advice: prefer no inline comments (reported, not gated)

**Do**: name the function for what it does; put the reasoning in the review page.
```python
def flags_to_boolean(df):
    """Animal markers to booleans, tolerant of whitespace in source."""
```

**Don't**:
```python
df = df.dropna()  # drop the blanks because upstream sends empty strings
```

**Rationalizations**:
| Excuse | Reality |
|---|---|
| "A future reader needs to know why" | A comment gets one line and carries no evidence. The review page carries the rejected alternative, the rows that changed, and the assertion that guards it. |
| "This one is genuinely subtle" | Then it is too important for a comment. Subtle decisions go in the review page where they can be checked. |
| "Removing it loses information" | A comment asserting something false is worse than silence: it stops the next reader verifying. A wrong comment has negative value. |
| "It documents a gotcha in the data" | Data facts belong in `notes/findings/` with the query that establishes them, so they can be re-run. |

**Red flags**:
- Any `#` that is not `noqa`, `type:`, or a shebang
- A comment stating a number (`# 70 rows here`) with no way to re-derive it
- A comment explaining what the next line does

**Verification**:
- [ ] advisory PIPE001 findings have been read
- [ ] Docstrings state what a function does, not why a project decision was made
- [ ] Every numeric claim about the data lives in `notes/findings/` with its query

---

### Rule: every step reports what it changed

**Do**: rows in, rows out, delta, for each step, every run.
```
drop spurious columns          19,457 ->   19,457     +0   cols 35 -> 33
drop rows with no item name    19,457 ->   19,457     +0
```

**Don't**: write an artifact whose shape nobody printed.

**Rationalizations**:
| Excuse | Reality |
|---|---|
| "I checked it once interactively" | The next run is the one that silently drops 70 rows. The report is what makes a regression visible without anyone looking for it. |
| "The tests cover it" | Tests assert what you thought to assert. The report shows what actually happened, including what you did not predict. |
| "It's noisy" | Noise is a formatting problem. Losing a sixth of your rows unnoticed is a correctness problem. |

**Red flags**:
- `to_parquet` / `to_csv` in a function that prints nothing
- A step whose row delta has never been observed
- Reported counts that nobody would notice changing

**Verification**:
- [ ] `check_pipelines.py` reports no PIPE004
- [ ] Running any stage prints one line per step with in, out, and delta
- [ ] A deliberately broken step is visible in the output without reading code

---

## Enforcement

| Layer | Mechanism | Blocks |
|---|---|---|
| Write | `PostToolUse` hook (`.claude/hooks/pipe-gate.sh`, registered in `.claude/settings.json`) | the edit: violations go back to Claude to fix |
| Commit | `pipelines-gate` in `.pre-commit-config.yaml` | the commit |
| Merge | `check-pipelines` job in CI | the merge |

All three call the same script with the same exit semantics, so a rule cannot
hold in one place and lapse in another.

```bash
python correctness/checks/check_pipelines.py src scripts
```

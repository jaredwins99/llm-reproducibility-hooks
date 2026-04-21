---
name: judge
description: Invoke when you need subjective judgment on an artifact (agent output quality, code sensibility, protocol adherence). Spawns a judge subagent with a rubric.
---

# Judge

Use this skill when you need judgment that regex/heuristics can't capture.

## When to invoke

- Scoring agent outputs against a rubric (e.g., "is this Stan model reasonable?").
- Rating code quality, completeness, or adherence to protocol.
- Comparing two outputs to decide which is better on a subjective axis.

Do NOT use for objective checks (does it compile, are params in CI) — those stay as code.

## How it works

Spawn the `judge` subagent with:
1. The artifact to evaluate (file paths, raw text, whatever).
2. The rubric — explicit criteria with scoring scales.
3. What to return — structured JSON with scores + brief justifications.

The subagent runs in a fresh context with read-only tools. It cannot modify anything; it can only read and return structured output.

## Example invocation

```
Agent({
  subagent_type: "judge",
  description: "Score Stan model reasonableness",
  prompt: "Evaluate /tmp/eval-trial-42/model.stan against this rubric:\n\n- Uses non-centered parameterization where hierarchical (0-5)\n- Has weakly informative priors (not uniform) (0-5)\n- Uses vectorized operations where possible (0-5)\n- Overall: would a Stan expert consider this idiomatic? (0-5)\n\nReturn JSON: {scores: {...}, justifications: {...}, overall: 'pass|borderline|fail'}"
})
```

## Rubric guidelines

- Every criterion gets an explicit scale (0-5, 0-10, binary).
- Every criterion has an observable anchor ("uses keyword X", "shape is Y").
- Ask for justifications alongside scores. Single numbers are unauditable.
- Keep rubrics under 10 criteria. Longer rubrics reduce signal per criterion.

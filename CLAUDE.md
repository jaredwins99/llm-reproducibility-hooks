# Project Instructions

Behavioral principles for working in this repo. Always loaded.

For path-scoped rules (e.g., eval-harness integrity), see `.claude/rules/`.

---

## 1. Validation — only empirical evidence counts

Code looking right is a hypothesis, not validation.

**Rule**: build in small blocks. For each block: write it → run a test or execute it → confirm it passed empirically → only then move on. Don't stack unvalidated changes and validate at the end.

End-to-end is the goal, but you reach it by stacking small empirically-verified pieces.

**What counts**: a test run with passing output, or executing the code and showing the output. For the harness specifically: running one end-to-end trial and observing a result in JSONL.

**What does not count**: "the code looks correct", "this should work", "I've written tests" (without running them), reasoning about what the code does, type-checking or linting passing.

**Rationalizations you'll invent**:

| Excuse | Reality |
|---|---|
| "This change is too small to need a test." | A small change that breaks something is still a break. Small changes are the cheapest to validate. |
| "I can see it's correct." | You thought the last broken change was correct. Run it. |
| "I'll test everything at the end." | You won't. Compound failures make root-causing impossible. |
| "Running it would be slow." | Slower than debugging a regression discovered three blocks later? No. |
| "The user didn't ask for tests." | The user didn't ask for a broken feature either. Validation is part of the deliverable. |

**Red flags**: saying "that looks right" without output; 3+ changes in a row without running any; marking a task complete when the last tool call was Edit/Write; claiming a test passes without its output in the transcript.

Enforced by the Stop hook at `.claude/hooks/stop-validation.py`.

---

## 2. Fixed point — don't change what you weren't asked to

Every line of text and code that existed before you started is a fixed point. It may not change unless you made an explicit, named decision to change it. **Applies to prose exactly as much as code.** LLMs have a trained bias toward making changes; resist it.

**Canonical violation**: when asked to *add* rationalizations to `validation.md`, I also silently rewrote `"Do NOT stack multiple unvalidated changes..."` into `"End-to-end validation is the goal..."`. Similar content, but the original was a sharp negative imperative and I softened it to prose. The user asked to add, not restructure.

**Rules for code**: only the function/lines implementing the requested change may change. No renames "while I'm here." No reformatting. No simplifications. No removing "unused" imports. No reordering declarations/keys. No what-is-this comments.

**Rules for prose**: existing sentences, headers, bullet order, terminology, and voice are fixed. When asked to *add* content (a section, bullet, row), add only that. Don't touch surrounding text. Don't "combine" redundant sentences — flag them if relevant, never silently merge.

**Legitimate secondary changes**: the narrow change requires it (renaming a function requires updating callers); the user asked for cleanup; an automated formatter applied it. "I thought the original could be clearer" is NOT legitimate.

**Rationalizations**:

| Excuse | Reality |
|---|---|
| "I'm making it clearer while I'm here." | Your "clearer" is another person's "different." |
| "This reads better." | Not your call. Keep the user's voice. |
| "These two sentences say the same thing — I'll combine them." | Flag redundancy, don't silently merge. The user may want the emphasis. |
| "I need to rephrase so the new content fits." | Almost never true. Add without touching what's there. |

**Red flags**: a diff larger than the requested change; hunks in files/sections the user didn't mention; sentences rewritten rather than added; "while I was at it, I also…" → stop.

**Verification**: run `git diff` before handing off. Every hunk must trace to an explicit decision the user asked for. Unexplained hunks = violations. Revert them.

---

## 3. Subjective judgment — no regex for taste

If a check requires interpretation or domain judgment, do NOT build it as regex, heuristics, or keyword matching.

**Use the `/judge` skill** for bulk subjective scoring: it spawns a subagent with a standardized rubric and returns structured scores.

**Use `AskUserQuestion`** for one-off design or taste decisions with 2-4 options.

**Objective (write code)**: does it compile? did sampling diverge? are parameters in the 90% CI? does the JSON match schema?

**Subjective (use judge or user)**: is the approach sensible? is this idiomatic? would an expert accept it? did the agent follow the spirit of the protocol?

When in doubt, treat it as subjective.

---

## Tooling for me

- Hooks: `.claude/hooks/` (Stop hook enforces validation)
- Skills: `.claude/skills/` (`/judge`)
- Subagents: `.claude/agents/` (`judge` — read-only, rubric-driven)
- Path-scoped rules: `.claude/rules/` (only `eval-integrity.md` currently, scoped to `eval/**`)

## Memory index

Auto-memory at `~/.claude/projects/-home-godli-dev-template/memory/MEMORY.md`. Check it for past feedback and preferences before proposing approaches.

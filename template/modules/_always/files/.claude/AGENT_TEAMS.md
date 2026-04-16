# Agent Teams (Opt-In)

Agent teams allow multiple Claude agents to work in parallel with independent context windows and a shared task list.

## Enable

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

## When to Use

**Good for:**
- Parallel code review (each agent checks different rules/files)
- Large refactors where agents own separate files
- Research tasks investigating different angles simultaneously

**Avoid for:**
- Sequential tasks
- Same-file edits (risk of overwrites)
- Simple tasks (higher token cost)

## Recommended Team Patterns

### Parallel Review (3 agents)
- Agent 1: style rules (comments, naming, separators)
- Agent 2: pipeline conventions (chaining, logging, no loops)
- Agent 3: security/defensive coding

### Parallel Refactor (3 agents)
- Agent 1: extract functions from scripts/ to src/
- Agent 2: update imports in affected files
- Agent 3: write tests for extracted functions

## Team Size
3-5 agents optimal. Give each agent clear file ownership to avoid conflicts.

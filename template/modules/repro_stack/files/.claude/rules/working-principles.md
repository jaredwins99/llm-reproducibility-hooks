# Working principles (always loaded)

@PRINCIPLES.md

## For Claude specifically

- Before saying anything works, run the command that would show it does not
  and show its output: `make gate`, `make test`, `make notes`, or the
  specific stage. `make check` runs all three.
- The PostToolUse hook runs the pipe gate on every Python file you write in a
  gated directory. When it blocks, fix the code. Never add `# noqa`, move the
  file, edit the checker, or pass `--no-verify`.
- Do not install packages ad hoc. Import the package, then `make pin` so
  `environment.yml` and `renv.lock` stay the single source of truth.
- Commit messages: no attribution lines, no reference to the user or to
  yourself. A PreToolUse hook refuses commits that break this.
- If something cannot be found quickly, ask instead of searching at length.

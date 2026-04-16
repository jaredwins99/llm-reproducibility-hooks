---
description: Data pipeline conventions
globs: ["scripts/**/*.py", "scripts/**/*.R"]
---

# Pipeline Conventions

## Script structure

Bare pipeline at script level. Do not wrap the pipeline in a `main()` function or `if __name__` guard.
The script is the pipeline. Run it, it does the thing.

## Chaining

Chain everything. Avoid intermediate variables for data frames mid-pipeline.
Each step should flow into the next via method chaining (`.pipe()`, `%>%`, `|>`).

## Custom transforms

Use `.pipe()` for custom transform functions. Use accessor extensions (`px`) for operations pandas does not provide natively.

## Compute defaults

Default to pandas. Migrate to dask only when the dataset exceeds 50% of available RAM or runtime exceeds 5 minutes.
Do not prematurely optimize for scale.

## Output format

Write to parquet, not CSV. Parquet preserves types, compresses well, and reads faster.
Use CSV only for human-inspectable debug output or external delivery requirements.

## Preamble

Every pipeline script starts with the project preamble import:

```python
from project.preamble import *
```

This sets up logging, paths, and shared configuration. Do not duplicate that setup manually.

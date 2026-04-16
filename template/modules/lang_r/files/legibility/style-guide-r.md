
# === R-Specific Style ===

## Pipe operator
Both `%>%` (magrittr) and `|>` (native) are allowed. Prefer `%>%` when you need the `.` placeholder for inline logging (`{. %>% print(); .}`). The native pipe doesn't support `.` or `{}` blocks.

## Always end chains with identity()
Every pipe chain must end with `identity()`. This lets you comment out any line without causing a trailing pipe error.

```r
# GOOD:
result <- df %>%
  filter(x > 0) %>%
  mutate(y = x + 1) %>%
  identity()

# Now you can safely comment out the last real step:
result <- df %>%
  filter(x > 0) %>%
  # mutate(y = x + 1) %>%
  identity()
```

## Inline logging
Use the `.` placeholder for inline logging without breaking the chain:

```r
result <- df %>%
  filter(x > 0) %>%
  {. %>% nrow() %>% paste("rows after filter:") %>% print(); .} %>%
  mutate(y = x + 1) %>%
  identity()
```

Or use a helper:
```r
print_rows <- function(df) {
  cat(paste("# of rows:", nrow(df), "\n"))
  df
}
```

## Tidyverse verbs over base R
Prefer tidyverse equivalents: `read_csv` over `read.csv`, `filter` over `subset`, `map` over `sapply`. The linter enforces this.

## Braces
Default: closing brace on the same line as the last statement. `} else {` must always be on one line (R parser requirement).

```r
# Default style:
if (x > 0) {
    y <- 1
} else {
    y <- 2}

for (i in seq_along(items)) {
    process(items[[i]])}
```

This is a changeable setting — switch to tidyverse style (closing brace on own line) by setting `brace_linter(allow_single_line = FALSE)` in `.lintr`.

## Assignment
Always use `<-` for assignment, never `=`.

## Paths
Always use `file.path()` for constructing paths. Never use `'/'` or `'\\'` string concatenation. This ensures cross-OS compatibility.

```r
# GOOD:
file.path(DATA_DIR, 'v001', 'raw.parquet')

# BAD:
paste0(DATA_DIR, '/v001/raw.parquet')
```

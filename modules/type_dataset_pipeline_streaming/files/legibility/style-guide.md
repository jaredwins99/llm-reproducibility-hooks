
# === Data Pipeline Style ===

## The Pipeline Philosophy

Everything is a data transformation. A pipeline takes one data structure and converts it to another. There are no loops — only maps. If you find yourself writing a `for` loop over rows, you're doing it wrong. If you find yourself writing a `for` loop over columns, functionalize the body and map it.

## Core Rules

### 1. Chains, not variables
Prefer one continuous chain from input to output. Intermediate variables break the flow and invite mutation bugs.

**Good:**
```python
result = (
    pd.read_parquet('input.parquet')
    .dropna(subset=['id'])
    .assign(revenue=lambda df: df['price'] * df['qty'])
    .groupby('category')
    .agg({'revenue': 'sum'})
)
```

**Bad:**
```python
df = pd.read_parquet('input.parquet')
df = df.dropna(subset=['id'])
df['revenue'] = df['price'] * df['qty']
grouped = df.groupby('category')
result = grouped.agg({'revenue': 'sum'})
```

### 2. Bare pipeline at script level
The outermost pipeline should NOT be wrapped in a function. This allows you to:
- Run the script and see results immediately
- Comment out `.pipe()` steps to debug
- Inspect intermediate state interactively

**Good:**
```python
# scripts/02_transform.py
model_data = (
    pd.read_parquet(DATA_DIR / 'raw.parquet')
    .pipe(clean_dates)
    .pipe(add_outcomes)
    .pipe(add_time_variables)
)
model_data.to_parquet(DATA_DIR / 'model_data.parquet')
```

**Bad:**
```python
def transform():
    return pd.read_parquet(...).pipe(...)

if __name__ == '__main__':
    transform()
```

### 3. Extract functions only when needed
Base pandas is legible. But stringing together too many base pandas operations leads to errors. Extract into `.pipe()`-able functions when:
- A section is more than ~10 chained operations
- The logic is reused across scripts
- The logic needs its own tests

Keep extracted functions in `src/` so they're importable and testable.

### 4. Log every change
After every transformation step that changes the shape or content of data, print or log the result. This is not optional — it's how you catch silent data loss.

```python
result = (
    raw_data
    .pipe(lambda df: print(f'Raw: {df.shape[0]} rows') or df)

    .dropna(subset=['id'])
    .pipe(lambda df: print(f'After dropna: {df.shape[0]} rows') or df)

    .pipe(add_features)
    .pipe(lambda df: print(f'After features: {df.shape}') or df)
)
```

A utility helper `log_step(msg)` is available in `src/` for cleaner syntax:
```python
from {{project_name}}.core.pipeline import log_step

result = (
    raw_data
    .pipe(log_step('Raw'))
    .dropna(subset=['id'])
    .pipe(log_step('After dropna'))
)
```

### 5. No loops — use maps
If you need to apply the same pipeline to multiple columns/groups/files, don't loop. Functionalize the pipeline body and map.

**Good:**
```python
def build_exposure(daily_model, col):
    return (
        daily_model
        .pipe(compute_pivot, col=col)
        .pipe(log_step(f'{col} exposure'))
    )

exposure_tables = {
    col: build_exposure(daily_model, col)
    for col in DISHES_COUNT_COLS
}
```

**Bad:**
```python
for col in DISHES_COUNT_COLS:
    result = daily_model.pipe(compute_pivot, col=col)
    result.to_parquet(...)
```

### 6. Comment sections within chains
Use `#` comments to label logical sections of a long chain. This makes the pipeline scannable.

```python
model_data = (
    raw
    # Outcomes
    .assign(
        vegan_outcome=lambda df: 1 * df['vegan'],
        total_outcome=1)

    # Locations
    .astype({'location_id': 'category'})

    # Time variables
    .set_index('created_at')
    .pipe(add_intraday_variables)
    .pipe(add_interday_variables)
)
```

### 7. Default to pandas — know when to migrate
Start with pandas. Migrate to dask when either threshold is hit:
- **RAM**: Dataset exceeds ~50% of available system memory
- **Time**: A single pipeline script takes more than 5 minutes to run

The pipeline structure stays the same — only the engine changes. Dask DataFrames support the same `.assign()`, `.pipe()`, `.groupby()` API. The migration should be mechanical, not architectural.

### 8. Use accessors for things pandas doesn't have
Register custom pandas accessors in `src/` for operations that don't exist natively — like `.print()` for inline logging without breaking the chain. Don't wrap every function as an accessor; only add them when they avoid breaking out of pipeline mode.

```python
# src/{{project_name}}/core/accessors.py
@pd.api.extensions.register_dataframe_accessor('px')
class PxAccessor:
    def __init__(self, df):
        self._df = df

    def print(self, msg=''):
        print(f'{msg}: {self._df.shape[0]} rows x {self._df.shape[1]} cols')
        return self._df

# In a script — stays in pipeline mode
import {{project_name}}.core.accessors

result = (
    raw_data
    .dropna(subset=['id'])
    .px.print('After dropna')
    .assign(revenue=lambda df: df['price'] * df['qty'])
    .px.print('After assign')
)
```

**When to use accessors:** When you'd otherwise have to break out of the pipeline because no native pandas method exists. Never use monkey patching — accessors are the proper extension mechanism.

### 9. Write to parquet
Prefer `.parquet` over `.csv` for all intermediate and output data. It preserves types, compresses well, and is fast to read/write.

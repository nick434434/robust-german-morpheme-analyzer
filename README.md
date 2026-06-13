# Morpheme Analysis

## Development

Install dependencies and create the local virtual environment:

```bash
uv sync --dev
```

Run tooling through the uv-managed environment:

```bash
uv run ruff format .
uv run ruff check .
uv run basedpyright --project .
uv run pytest
```

## Run Configurations

### `main`

```bash
PYTHONUNBUFFERED=1 uv run python main.py
```

Runs the current morpheme analyzer against the no-subcluster input files under
`inputs_no_subclaster_names/`.

Outputs:

- `ecology_new_roots.csv`
- `economy_new_roots.csv`
- `sociology_new_roots.csv`
- `all_sources_new_roots.csv`

### `main_v1`

```bash
PYTHONUNBUFFERED=1 uv run python main_v1.py
```

Runs the first analyzer variant over the files in `inputs/`.

Outputs per-input CSVs under `morphology_stats_v1/`, plus
`morphology_stats_v1/all_sources.csv`.

### `main_v2`

```bash
PYTHONUNBUFFERED=1 uv run python main_v2.py
```

Runs the second analyzer variant over the files in `inputs/`, then aggregates
ecology, economy, sociology, and full-corpus results.

Outputs per-input CSVs and aggregate CSVs under `morphology_stats/`.

### `count_frequencies`

```bash
PYTHONUNBUFFERED=1 uv run --project . --directory frequency_count python count_frequencies.py
```

Runs root-frequency counting from the `frequency_count/` working directory, matching
the PyCharm config. It reads transcript text files in `frequency_count/` and root CSVs
from the project root.

Outputs frequency CSVs in `frequency_count/` for ecology, economy, and sociology.
The script currently uses `limit = 4`.

### `test_split`

```bash
PYTHONUNBUFFERED=1 uv run python test_split.py
```

Runs the split diagnostic script PyCharm was configured for. This is not a proper
pytest assertion suite yet; it prints expected and actual values and reports `PASS` or
`FAIL` manually.

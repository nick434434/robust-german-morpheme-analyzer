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

### Current Analyzer

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis analyze current
```

Runs the current morpheme analyzer against the no-subcluster input files under
`data/inputs_no_subcluster_names/`.

Outputs:

- `results/roots/ecology_new_roots.csv`
- `results/roots/economy_new_roots.csv`
- `results/roots/sociology_new_roots.csv`
- `results/roots/all_sources_new_roots.csv`

### Analyzer V1

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis analyze v1
```

Runs the first analyzer variant over the files in `data/inputs/`.

Outputs per-input CSVs under `results/morphology_stats_v1/`, plus
`results/morphology_stats_v1/all_sources.csv`.

### Analyzer V2

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis analyze v2
```

Runs the second analyzer variant over the files in `data/inputs/`, then aggregates
ecology, economy, sociology, and full-corpus results.

Outputs per-input CSVs and aggregate CSVs under `results/morphology_stats/`.

### Frequency Counting

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis frequencies --limit 4
```

Runs root-frequency counting. It reads transcript text files from `data/transcripts/`
and root CSVs from `results/roots/`.

Outputs frequency CSVs in `results/frequency_count/` for ecology, economy, and
sociology.

### Split Diagnostic

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis diagnostic split
```

Runs the split diagnostic script PyCharm was configured for. This is not a proper
pytest assertion suite yet; it prints expected and actual values and reports `PASS` or
`FAIL` manually.

### Midword Diagnostic

```bash
PYTHONUNBUFFERED=1 uv run morpheme-analysis diagnostic midword
```

Runs the midword chunk diagnostic script. Like the split diagnostic, it is print-based
and not a proper pytest assertion suite yet.

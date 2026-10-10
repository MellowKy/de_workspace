# Production Incident Response Playbook

## Incident Scenario 1: GitHub REST API Rate Limiting (HTTP 403)
- **Symptom:** CI pipeline stage 'Pre-Generate Data Lake Parquet Files' returns HTTP 403.
- **Root Cause:** Runner shared IP address exceeded unauthenticated limit (60 req/hr).
- **Remediation Procedure:**
  1. Confirm `GITHUB_TOKEN` secret is passed to environment step in `.github/workflows/data_pipeline_ci.yml`.
  2. Verify fallback synthetic record generator activates in `realtime_lakehouse.py`.
  3. Re-run failed CI job non-interactively: `gh run rerun <RUN_ID>`.

## Incident Scenario 2: Schema Drift in Raw Parquet Streams
- **Symptom:** DuckDB throws 'Binder Error: Column not found' during `dbt run`.
- **Root Cause:** Upstream ingestion API altered nested JSON field definitions.
- **Remediation Procedure:**
  1. Inspect Parquet footers via CLI: `uv run --no-project python3 -c "import polars as pl; print(pl.read_parquet('.data_scratch/processed/parquet/*.parquet').schema)"`.
  2. Ensure `read_parquet()` in staging queries handles union types gracefully.
  3. Re-execute local verification suite: `python3 scripts/verify_monorepo.py`.

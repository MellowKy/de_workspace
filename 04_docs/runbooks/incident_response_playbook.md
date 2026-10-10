# Production Incident Response & Recovery Runbook

## Incident Scenario 1: GitHub REST API Rate Limiting (HTTP 403)
- **Symptom:** CI pipeline stage `Pre-Generate Data Lake Parquet Files` or Dagster materialization returns HTTP 403.
- **Root Cause:** Runner shared IP address exceeded GitHub unauthenticated limit (60 req/hr).
- **Remediation Procedure:**
  1. Confirm `GITHUB_TOKEN` secret is passed to environment step in `.github/workflows/data_pipeline_ci.yml`.
  2. Verify fallback synthetic record generator activates in `realtime_lakehouse.py`.
  3. Re-run failed CI job non-interactively: `gh run rerun <RUN_ID>`.

## Incident Scenario 2: Schema Drift in Raw Parquet Files
- **Symptom:** DuckDB throws `Binder Error: Column not found` during `dbt run`.
- **Root Cause:** Upstream ingestion engine renamed nested JSON fields.
- **Remediation Procedure:**
  1. Inspect Parquet footers via CLI: `uv run --no-project python3 -c "import polars as pl; print(pl.read_parquet('.data_scratch/processed/parquet/*.parquet').schema)"`.
  2. Ensure `read_parquet()` in `stg_github_events.sql` utilizes `union_by_name=True`.
  3. Re-execute local verification suite: `python3 scripts/verify_monorepo.py`.

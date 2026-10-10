# Disaster Recovery & Backfill Playbook

## Executive Summary & SLA Metrics
- **Recovery Time Objective (RTO):** < 15 Minutes
- **Recovery Point Objective (RPO):** < 1 Hour (Incremental Stream Catch-up)

---

## Disaster Scenario 1: Total Storage Scratch Corruption
- **Trigger:** System crash or disk corruption invalidates `.data_scratch/` Parquet files.
- **Impact:** Downstream dbt models and Dagster assets fail to read raw Parquet files.

### Step-by-Step Remediation Sequence
1. Re-initialize raw streaming buffer and Parquet sink:
   ```bash
   uv run --no-project python3 03_projects/05_realtime_lakehouse/realtime_lakehouse.py
   ```
2. Execute atomic Dagster Software-Defined Asset re-materialization:
   ```bash
   uv run --no-project dagster asset materialize --select "*" -f 03_projects/06_dagster_orchestration/repository.py
   ```
3. Validate data integrity assertions via dbt:
   ```bash
   cd 03_projects/02_elt_duckdb_dbt
   uv run --no-project dbt run --profiles-dir ~/.dbt
   uv run --no-project dbt test --profiles-dir ~/.dbt
   cd ~/de_workspace
   ```

---

## Disaster Scenario 2: DuckDB Lock & State Desynchronization
- **Trigger:** Process interrupted abruptly leaving `.duckdb.wal` lock files open.
- **Remediation Procedure:**
  1. Terminate orphaned DuckDB instances: `pkill -f duckdb`
  2. Clean transient lock files: `rm -f .data_scratch/*.wal`
  3. Re-execute local verification suite: `python3 scripts/verify_monorepo.py`

# ADR-003: Dagster Software-Defined Assets vs Apache Airflow Imperative DAGs

- **Status:** Accepted
- **Date:** 2026-10-10
- **Context:** Pipeline orchestration requires tracking data materialization state, schema lineage, and operational metrics.

## Decision
We selected **Dagster Software-Defined Assets (SDAs)** over traditional **Apache Airflow imperative DAGs**.

## Rationale
1. **Asset-Centric Paradigm:** Maps execution targets directly to physical storage outputs (`raw_events` -> `stg_parquet` -> `fct_mart`).
2. **Embedded Vector Metadata:** Integrated logging allowed embedding materialization telemetry (row counts, file sizes) into Qdrant vector indices.
3. **Zero Daemon Overhead:** Assets materialize headlessly via `dagster asset materialize` without requiring persistent web servers or Postgres metadata databases.

## Consequences
- **Positive:** Declarative data lineage, unit-testable asset functions, built-in metadata inspection.
- **Negative:** Requires team mindset shift from task scheduling (`task_a >> task_b`) to asset state reconciliation.

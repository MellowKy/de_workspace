# ADR-002: Embedded DuckDB + dbt vs Snowflake for Analytical Marts

- **Status:** Accepted
- **Date:** 2026-10-10
- **Context:** Modeling raw lakehouse Parquet files into Kimball Star Schema marts requires dbt SQL transformations and automated data assertions.

## Decision
We selected **embedded DuckDB (`dbt-duckdb`)** over cloud-hosted analytical warehouses (Snowflake / BigQuery) for core dimensional modeling.

## Rationale
1. **Zero-Copy Parquet Scanning:** DuckDB reads Parquet file footers directly via `read_parquet()`, avoiding costly cloud data loading (COPY INTO) steps.
2. **Cost Optimization (FinOps):** Runs analytical queries locally or inside GitHub Actions runners with $0 credit spend.
3. **Full dbt Feature Parity:** Supports dbt models, macros, testing, custom schema assertions, and profile targets seamlessly.

## Consequences
- **Positive:** Rapid local testing cycle (< 200ms compile/run time), lightweight memory usage (< 30 MB RAM).
- **Negative:** Concurrent write operations require connection locking, necessitating read-replica abstractions for multi-user BI workloads.

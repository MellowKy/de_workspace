# Enterprise Portable Data Platform (EPDP) Monorepo

An enterprise-grade, lightweight data engineering workspace demonstrating end-to-end data platform engineering, streaming ingestion, lakehouse modeling, IaC, asset orchestration, and AI-driven vector governance.

## Architecture Highlights
- **Engine Layer:** Out-of-core DuckDB + Polars LazyFrames (Zero heavy compute overhead).
- **Modeling Layer:** dbt Star Schema (Kimball Methodology) with custom schema assertions.
- **Orchestration:** Dagster Software-Defined Assets (SDAs) replacing imperative DAGs.
- **AI Vector Catalog:** Qdrant in-memory vector index logging asset lineage and run telemetry.
- **Infrastructure:** Terraform HCL modules for AWS S3 lakehouse deployment.
- **DevOps/CI/CD:** GitHub Actions with deterministic `uv.lock` dependency layer caching.

## Portfolio Module Breakdown
| Module | Technical Focus | Business Value |
| :--- | :--- | :--- |
| `01_cli_linux_wrangling` | POSIX parallel processing (`xargs`, `awk`) | Ingests raw streams at wire-speed with $0 compute cost |
| `02_elt_duckdb_dbt` | DuckDB + dbt Kimball Star Schema | Standardizes raw data into structured business marts |
| `03_devops_terraform_cicd` | Terraform IaC & GitHub Actions | Automated, repeatable multi-environment cloud infrastructure |
| `05_realtime_lakehouse` | Polars LazyFrames + ZSTD Parquet | High-throughput real-time lakehouse transformation |
| `06_dagster_orchestration` | Dagster SDAs + Qdrant Vector Index | AI-ready metadata governance and vector lineage search |

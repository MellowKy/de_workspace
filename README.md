# Enterprise Portable Data Platform (EPDP) Monorepo

[![Data Engineering CI/CD Pipeline](https://github.com/MellowKy/de_workspace/actions/workflows/data_pipeline_ci.yml/badge.svg)](https://github.com/MellowKy/de_workspace/actions/workflows/data_pipeline_ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![uv](https://img.shields.io/badge/package_manager-uv-purple.svg)
![DuckDB](https://img.shields.io/badge/lakehouse-DuckDB-yellow.svg)
![dbt](https://img.shields.io/badge/modeling-dbt--duckdb-orange.svg)
![Dagster](https://img.shields.io/badge/orchestration-Dagster_SDA-red.svg)
![Qdrant](https://img.shields.io/badge/vector_db-Qdrant-red.svg)
![Terraform](https://img.shields.io/badge/IaC-Terraform_1.9.5-purple.svg)

An enterprise-grade, zero-compute-cost data platform monorepo demonstrating end-to-end platform engineering, out-of-core lakehouse processing, declarative IaC, software-defined asset orchestration, DevSecOps SAST governance, and AI-driven vector schema cataloging.

---

## 🏛️ Platform Architecture Overview

```
 [ Ingestion Layer ]        [ Lakehouse & Modeling ]       [ Orchestration & Governance ]
 Polars LazyFrames      ──> DuckDB + dbt Star Schema  ──> Dagster SDAs + Qdrant Vector Index
 (ZSTD Parquet Sinks)       (Kimball Data Marts)          (AI Semantic Schema Catalog)
```

---

## 📦 Monorepo Module Matrix

| Module | Core Technology | Architectural Pattern | Business & Platform Value |
| :--- | :--- | :--- | :--- |
| **`01_cli_linux_wrangling`** | POSIX `xargs`, `awk`, `sed` | Parallel Stream Extraction | Wire-speed raw parsing with $0 compute overhead |
| **`02_elt_duckdb_dbt`** | DuckDB, dbt, SQLFluff | Kimball Star Schema Modeling | Reconciles raw lakehouse files into tested analytical marts |
| **`03devops_terraform_cicd`** | Terraform 1.9.5, GitHub Actions | Declarative Infrastructure | Multi-environment AWS S3 data lake provisioning with AES256 |
| **`05_realtime_lakehouse`** | Polars LazyFrames, PyArrow | Out-of-Core Stream Sinking | Memory-safe, high-throughput Parquet lakehouse engine |
| **`06_dagster_orchestration`** | Dagster, `qdrant-client` | Software-Defined Assets | Declarative lineage tracking & vector run logging |
| **`scripts/ai_catalog_query.py`** | Qdrant `query_points` API | Vector-Driven Governance | AI-ready natural language schema and lineage search |
| **`scripts/verify_monorepo.py`** | Python `subprocess`, `bandit` | Shift-Left DevSecOps Testing | Single-command health check across all 8 platform gates |

---

## ⚡ Quickstart & Local Verification

### 1. Environment Setup
```bash
git clone https://github.com/MellowKy/de_workspace.git
cd de_workspace
source .venv/bin/activate
uv sync --no-install-project
```

### 2. Execute Full Platform Health Check Suite
```bash
python3 scripts/verify_monorepo.py
```

### 3. Query the AI Schema Catalog
```bash
python3 scripts/ai_catalog_query.py --query "actor activity engagement"
```

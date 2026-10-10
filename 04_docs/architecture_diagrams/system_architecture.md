# Enterprise Data Platform Topology & Lineage

## End-to-End System Lineage Diagram

```mermaid
graph TD
    A[GitHub REST API] -->|Stream Buffer| B[raw_events.ndjson]
    B -->|Polars LazyFrame Sinker| C[github_events_stream.parquet]
    C -->|read_parquet / DuckDB| D[stg_github_events View]
    D -->|dbt Transformations| E[fct_github_activity Mart]
    E -->|Telemetry Extraction| F[Qdrant In-Memory Vector Catalog]
    G[Terraform HCL 1.9.5] -->|Provisioning| H[AWS S3 Data Lake Bucket]
```

## Infrastructure & Compute Layers
- **Ingestion:** Native HTTP requests with exponential fallbacks to Polars streaming sinks.
- **Lakehouse Processing:** Embedded DuckDB in-memory OLAP engine reading ZSTD Parquet buffers.
- **Modeling & Testing:** dbt core transformations with schema validation assertions.
- **Orchestration:** Dagster Software-Defined Assets (SDAs) tracking materialization state.
- **AI Observability:** Qdrant vector collection indexing run payloads and schema embeddings.

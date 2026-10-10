# ADR-001: Polars LazyFrames vs PySpark for Edge Stream Ingestion

- **Status:** Accepted
- **Date:** 2026-10-10
- **Context:** High-throughput JSON stream ingestion required an out-of-core transformation engine capable of running on edge hardware without JVM overhead.

## Decision
We selected **Polars LazyFrames** over **PySpark** for real-time Parquet lakehouse stream ingestion.

## Rationale
1. **Memory Efficiency:** Polars operates via Rust memory management without JVM overhead, keeping RAM consumption < 50 MB on Apple Silicon and Linux runners.
2. **Out-of-Core Execution:** `pl.scan_ndjson` and `sink_parquet` process streams out-of-core without loading raw NDJSON buffers eagerly into system RAM.
3. **Zero Cluster Overhead:** Avoids local or cloud PySpark cluster setup while maintaining native Arrow and ZSTD Parquet vectorization.

## Consequences
- **Positive:** Instant startup time (< 20ms), $0 compute execution costs, simple local testing.
- **Negative:** Multi-node distributed computing requires migrating execution logic to Apache Arrow / Ray if data volumes exceed single-node disk capacity.

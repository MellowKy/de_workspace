import json
import os
import sys
from pathlib import Path

import duckdb
import polars as pl
import requests


def run_realtime_pipeline():
    print("==================================================")
    print(" Module 5: Dynamic Real-Time Stream Ingestion     ")
    print("==================================================")

    # Dynamic workspace root calculation relative to script location
    WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

    # Environment variable overrides with fallback defaults
    SCRATCH_DIR = Path(os.getenv("DE_SCRATCH_DIR", WORKSPACE_ROOT / ".data_scratch"))

    raw_dir = SCRATCH_DIR / "raw" / "streaming"
    proc_dir = SCRATCH_DIR / "processed" / "parquet"

    raw_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)

    buffer_file = raw_dir / "event_stream_buffer.ndjson"
    output_parquet = proc_dir / "github_events_stream.parquet"

    # Step 1: Ingest payload and write strict RFC 8259 NDJSON
    print(f"==> Step 1: Ingesting GitHub API stream into {buffer_file}...")
    response = requests.get(
        "https://api.github.com/repos/apache/spark/events?per_page=100"
    )
    if response.status_code != 200:
        print(f"[ERROR] API Request failed with status code {response.status_code}")
        sys.exit(1)

    events = response.json()
    with open(buffer_file, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(event) + "\n" for event in events)

    print(f"[OK] Buffered {len(events)} strict NDJSON records.")

    # Step 2: Polars LazyFrame Stream Transformation Engine
    print("\n==> Step 2: Executing Polars LazyFrame streaming engine...")
    lazy_stream = (
        pl.scan_ndjson(str(buffer_file))
        .select(
            [
                pl.col("id").cast(pl.String).alias("event_id"),
                pl.col("type").alias("event_type"),
                pl.col("actor").struct.field("login").alias("actor_username"),
                pl.col("repo").struct.field("name").alias("repository_name"),
                pl.col("created_at")
                .str.to_datetime(time_zone="UTC")
                .alias("event_timestamp"),
            ]
        )
        .with_columns(
            [
                pl.col("event_timestamp").dt.date().alias("event_date"),
                pl.col("event_timestamp").dt.time().alias("event_time"),
            ]
        )
    )

    lazy_stream.sink_parquet(str(output_parquet), compression="zstd")
    file_size_kb = os.path.getsize(output_parquet) / 1024
    print(
        f"[OK] Stream sink complete. Generated Parquet: {output_parquet} ({file_size_kb:.2f} KB)"
    )

    # Step 3: Out-of-Core DuckDB Query
    print("\n==> Step 3: Querying Parquet Lakehouse via DuckDB...")
    con = duckdb.connect()
    query = f"""
        SELECT 
            event_type,
            COUNT(*) AS total_events,
            COUNT(DISTINCT actor_username) AS distinct_actors
        FROM read_parquet('{output_parquet}')
        GROUP BY event_type
        ORDER BY total_events DESC
        LIMIT 5;
    """
    results = con.execute(query).fetchall()

    print(f"{'EVENT TYPE':<25} | {'TOTAL EVENTS':<12} | {'DISTINCT ACTORS':<15}")
    print("-" * 60)
    for row in results:
        print(f"{row[0]:<25} | {row[1]:<12} | {row[2]:<15}")

    print("==================================================")
    print("[SUCCESS] Dynamic Streaming Lakehouse Pipeline Complete.")


if __name__ == "__main__":
    run_realtime_pipeline()

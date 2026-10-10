import os
import sys
import json
import requests
import polars as pl
import duckdb

def run_realtime_pipeline():
    print("==================================================")
    print(" Module 5: Real-Time Stream Ingestion & Lakehouse ")
    print("==================================================")

    scratch_raw = os.path.expanduser("~/de_workspace/.data_scratch/raw/streaming")
    scratch_proc = os.path.expanduser("~/de_workspace/.data_scratch/processed/lakehouse")
    os.makedirs(scratch_raw, exist_ok=True)
    os.makedirs(scratch_proc, exist_ok=True)

    buffer_file = os.path.join(scratch_raw, "event_stream_buffer.ndjson")
    output_parquet = os.path.join(scratch_proc, "github_events_stream.parquet")

    # Step 1: Wipe existing buffer file if present
    if os.path.exists(buffer_file):
        os.remove(buffer_file)

    print("==> Step 1: Ingesting GitHub API stream into strict NDJSON...")
    response = requests.get("https://api.github.com/repos/apache/spark/events?per_page=100")
    if response.status_code != 200:
        print(f"[ERROR] API Request failed with status code {response.status_code}")
        sys.exit(1)

    events = response.json()
    
    # Write strict RFC 8259 JSON lines using json.dumps()
    with open(buffer_file, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    print(f"[OK] Buffered {len(events)} strict NDJSON records to {buffer_file}")

    # Step 2: Polars LazyFrame Streaming Transformation Engine
    print("\n==> Step 2: Executing Polars LazyFrame streaming engine...")
    lazy_stream = (
        pl.scan_ndjson(buffer_file)
        .select([
            pl.col("id").cast(pl.String).alias("event_id"),
            pl.col("type").alias("event_type"),
            pl.col("actor").struct.field("login").alias("actor_username"),
            pl.col("repo").struct.field("name").alias("repository_name"),
            pl.col("created_at").str.to_datetime().alias("event_timestamp"),
        ])
        .with_columns([
            pl.col("event_timestamp").dt.date().alias("event_date"),
            pl.col("event_timestamp").dt.time().alias("event_time")
        ])
    )

    # Sink directly to ZSTD Parquet out-of-core
    lazy_stream.sink_parquet(output_parquet, compression="zstd")
    file_size_kb = os.path.getsize(output_parquet) / 1024
    print(f"[OK] Stream sink complete. Generated Parquet: {output_parquet} ({file_size_kb:.2f} KB)")

    # Step 3: Zero-RAM OLAP Queries via DuckDB
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
    print("[SUCCESS] Real-Time Lakehouse Pipeline Complete.")

if __name__ == "__main__":
    run_realtime_pipeline()

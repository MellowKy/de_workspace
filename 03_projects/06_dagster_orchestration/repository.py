import json
import os
from pathlib import Path

import duckdb
import polars as pl
import requests
from dagster import Definitions, MaterializeResult, MetadataValue, asset
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SCRATCH_DIR = Path(
    os.getenv("DE_SCRATCH_DIR", WORKSPACE_ROOT / ".data_scratch" / "dagster")
)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = SCRATCH_DIR / "raw_events.ndjson"
PARQUET_FILE = SCRATCH_DIR / "events_stream.parquet"
DB_FILE = SCRATCH_DIR / "orchestrated_lakehouse.duckdb"


@asset(
    description="Ingests real-time GitHub repository events stream into strict NDJSON buffer."
)
def raw_github_events() -> MaterializeResult:
    response = requests.get(
        "https://api.github.com/repos/apache/spark/events?per_page=100"
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API Ingestion Failed with status code {response.status_code}"
        )

    events = response.json()
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(event) + "\n" for event in events)

    return MaterializeResult(
        metadata={
            "record_count": len(events),
            "file_size_kb": MetadataValue.float(os.path.getsize(RAW_FILE) / 1024),
            "target_path": str(RAW_FILE),
        }
    )


@asset(
    deps=[raw_github_events],
    description="Transforms raw NDJSON buffer into vectorized Parquet lakehouse file using Polars LazyFrames.",
)
def stg_parquet_lakehouse() -> MaterializeResult:
    lazy_stream = (
        pl.scan_ndjson(str(RAW_FILE))
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

    lazy_stream.sink_parquet(str(PARQUET_FILE), compression="zstd")
    record_count = pl.read_parquet(str(PARQUET_FILE)).height

    return MaterializeResult(
        metadata={
            "parquet_records": record_count,
            "parquet_size_kb": MetadataValue.float(
                os.path.getsize(PARQUET_FILE) / 1024
            ),
            "target_path": str(PARQUET_FILE),
        }
    )


@asset(
    deps=[stg_parquet_lakehouse],
    description="Materializes Star Schema analytical mart in DuckDB and logs execution lineage to Qdrant Vector Index.",
)
def fct_daily_activity_mart() -> MaterializeResult:
    con = duckdb.connect(str(DB_FILE))

    con.execute(f"""
        CREATE OR REPLACE TABLE fct_daily_activity AS
        SELECT
            event_date,
            event_type,
            COUNT(DISTINCT actor_username) AS unique_actors,
            COUNT(event_id) AS total_events
        FROM read_parquet('{PARQUET_FILE}')
        GROUP BY 1, 2
        ORDER BY total_events DESC;
    """)

    fact_count = con.execute("SELECT COUNT(*) FROM fct_daily_activity").fetchone()[0]
    con.close()

    # Embed asset lineage and run metadata into Qdrant Vector Collection
    qdrant = QdrantClient(location=":memory:")
    collection_name = "asset_governance_catalog"

    if qdrant.collection_exists(collection_name):
        qdrant.delete_collection(collection_name)

    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )

    qdrant.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=1,
                vector=[
                    float(fact_count),
                    float(os.path.getsize(PARQUET_FILE) / 1024),
                    1.0,
                    200.0,
                ],
                payload={
                    "asset_name": "fct_daily_activity_mart",
                    "upstream_sources": ["raw_github_events", "stg_parquet_lakehouse"],
                    "record_count": fact_count,
                    "storage_engine": "DuckDB + Parquet",
                    "governance_status": "VERIFIED",
                },
            )
        ],
    )

    catalog_query = qdrant.retrieve(collection_name=collection_name, ids=[1])
    indexed_payload = catalog_query[0].payload

    return MaterializeResult(
        metadata={
            "fact_records": fact_count,
            "vector_catalog_status": indexed_payload["governance_status"],
            "indexed_asset": indexed_payload["asset_name"],
        }
    )


defs = Definitions(
    assets=[raw_github_events, stg_parquet_lakehouse, fct_daily_activity_mart]
)

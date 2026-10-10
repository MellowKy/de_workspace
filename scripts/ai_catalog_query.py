import argparse

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def build_and_query_catalog(search_term: str):
    print("==================================================")
    print(" AI Data Architect: Vector Schema Search Engine  ")
    print("==================================================")

    qdrant = QdrantClient(location=":memory:")
    collection_name = "enterprise_schema_catalog"

    if qdrant.collection_exists(collection_name):
        qdrant.delete_collection(collection_name)

    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )

    # Indexed schema payloads from dbt and Dagster assets
    schema_records = [
        {
            "id": 1,
            "vector": [1.0, 0.2, 0.8, 0.1],
            "asset_name": "stg_github_events",
            "type": "dbt_staging_view",
            "description": "Cleaned staging view of raw GitHub events stream with standardized actor and repository columns.",
            "columns": [
                "event_id",
                "event_type",
                "actor_username",
                "repository_name",
                "event_date",
                "event_time",
            ],
        },
        {
            "id": 2,
            "vector": [0.1, 0.9, 0.3, 0.9],
            "asset_name": "fct_github_activity",
            "type": "dbt_fact_table",
            "description": "Aggregated daily user engagement mart tracking distinct actors and event counts.",
            "columns": [
                "event_date",
                "event_type",
                "unique_actors",
                "total_events",
            ],
        },
        {
            "id": 3,
            "vector": [0.8, 0.1, 0.9, 0.2],
            "asset_name": "raw_github_events",
            "type": "dagster_raw_asset",
            "description": "Ingested raw NDJSON event stream buffer extracted directly from GitHub REST API.",
            "columns": ["id", "type", "actor", "repo", "created_at"],
        },
    ]

    points = [
        PointStruct(id=r["id"], vector=r["vector"], payload=r) for r in schema_records
    ]
    qdrant.upsert(collection_name=collection_name, points=points)

    # Query matching vector representation
    query_vector = (
        [0.15, 0.85, 0.35, 0.85]
        if "actor" in search_term.lower()
        or "activity" in search_term.lower()
        or "user" in search_term.lower()
        else [0.9, 0.2, 0.8, 0.1]
    )

    # Execute vector similarity query using query_points (qdrant-client >= 1.10.0)
    response = qdrant.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=2,
    )
    results = response.points

    print(f"==> Search Query: '{search_term}'")
    print(f"{'MATCHED ASSET':<22} | {'SCORE':<7} | {'TYPE':<18} | {'COLUMNS'}")
    print("-" * 80)
    for res in results:
        payload = res.payload
        cols = ", ".join(payload["columns"][:3]) + "..."
        print(
            f"{payload['asset_name']:<22} | {res.score:.4f}  | {payload['type']:<18} | {cols}"
        )

    print("==================================================")
    print("[SUCCESS] Semantic Schema Search Completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Data Catalog Vector Search")
    parser.add_argument(
        "--query",
        type=str,
        default="actor activity engagement",
        help="Search query string",
    )
    args = parser.parse_args()
    build_and_query_catalog(args.query)

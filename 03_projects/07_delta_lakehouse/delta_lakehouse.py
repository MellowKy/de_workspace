import os
from pathlib import Path
import polars as pl
import duckdb
from deltalake import DeltaTable, write_deltalake

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DELTA_TABLE_PATH = WORKSPACE_ROOT / ".data_scratch" / "delta" / "github_events"
DELTA_TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

def run_delta_pipeline():
    print("==> [DELTA LAKE] Executing Versioned ACID Transactions...")

    raw_df_v0 = pl.DataFrame({
        "event_id": ["evt_101", "evt_102", "evt_103"],
        "event_type": ["PushEvent", "PullRequestEvent", "WatchEvent"],
        "actor": ["iceman", "mellowky", "octocat"],
        "repo": ["de_workspace", "de_workspace", "awesome-data"],
    })

    write_deltalake(
        table_or_uri=str(DELTA_TABLE_PATH),
        data=raw_df_v0.to_arrow(),
        mode="overwrite",
    )
    print("[OK] Delta Table Initialized (Version 0 Committed).")

    raw_df_v1 = pl.DataFrame({
        "event_id": ["evt_104", "evt_105"],
        "event_type": ["PushEvent", "IssuesEvent"],
        "actor": ["dev_ops", "qa_bot"],
        "repo": ["de_workspace", "de_workspace"],
        "payload_size_kb": [128.5, 42.0],
    })

    write_deltalake(
        table_or_uri=str(DELTA_TABLE_PATH),
        data=raw_df_v1.to_arrow(),
        mode="append",
        schema_mode="merge",
    )
    print("[OK] Delta Table Appended with Schema Evolution (Version 1 Committed).")

    con = duckdb.connect()
    con.execute("INSTALL delta; LOAD delta;")

    print("\n--- DuckDB Query: Current State (Version 1) ---")
    query = "SELECT event_id, event_type, actor, payload_size_kb FROM delta_scan(?)"
    v1_results = con.execute(query, [str(DELTA_TABLE_PATH)]).fetchall()
    for row in v1_results:
        print(row)

    dt = DeltaTable(str(DELTA_TABLE_PATH))
    print(f"\n[METADATA] Active Delta Table Version: {dt.version()}")
    print(f"[METADATA] Total Delta Commit Files: {len(dt.history())}")

if __name__ == "__main__":
    run_delta_pipeline()

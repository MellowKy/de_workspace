import json
import subprocess
import pyarrow as pa
import duckdb
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError
from deltalake import DeltaTable, write_deltalake
from dagster import asset, Definitions, MaterializeResult, in_process_executor
from governance.contracts.order_event import OrderContract

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STAGING_PATH = PROJECT_ROOT / "data/ingress/staging.jsonl"
BRONZE_DELTA_PATH = PROJECT_ROOT / "data/bronze/orders_delta"
SILVER_DELTA_PATH = PROJECT_ROOT / "data/silver/orders_delta"
GOLD_DELTA_PATH = PROJECT_ROOT / "data/gold/daily_sales_delta"
DLQ_PATH = PROJECT_ROOT / "data/dlq/orders_dlq.jsonl"
DBT_DIR = PROJECT_ROOT / "pipelines/processing/dbt"

@asset(group_name="bronze")
def raw_orders_bronze() -> MaterializeResult:
    BRONZE_DELTA_PATH.mkdir(parents=True, exist_ok=True)
    DLQ_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if STAGING_PATH.exists() and STAGING_PATH.stat().st_size > 0:
        with open(STAGING_PATH, "r") as f:
            incoming_payloads = [json.loads(line) for line in f if line.strip()]
        STAGING_PATH.unlink()
    else:
        incoming_payloads = [
            {"event_id": "evt-101", "timestamp": "2026-10-17T00:00:00Z", "customer_id": "cust-01", "amount": 149.99, "currency": "USD"},
            {"event_id": "evt-102", "timestamp": "2026-10-17T00:05:00Z", "customer_id": "cust-02", "amount": 89.50, "currency": "USD"},
            {"event_id": "evt-ERR", "timestamp": "INVALID_DATE", "customer_id": "cust-03", "amount": -20.00, "currency": "INVALID"}
        ]

    valid_records = []
    dlq_count = 0
    with open(DLQ_PATH, "a") as dlq_file:
        for payload in incoming_payloads:
            try:
                validated = OrderContract(**payload)
                record_dict = validated.model_dump()
                record_dict["timestamp"] = record_dict["timestamp"].isoformat()
                valid_records.append(record_dict)
            except (ValidationError, Exception) as err:
                dlq_count += 1
                dlq_record = {
                    "raw_payload": payload,
                    "error": str(err),
                    "failed_at": datetime.utcnow().isoformat()
                }
                dlq_file.write(json.dumps(dlq_record) + "\n")

    if valid_records:
        arrow_table = pa.Table.from_pylist(valid_records)
        write_deltalake(
            str(BRONZE_DELTA_PATH),
            arrow_table,
            mode="append"
        )
            
    return MaterializeResult(
        metadata={
            "valid_records_appended": len(valid_records),
            "dlq_records_isolated": dlq_count,
            "target_delta_table": str(BRONZE_DELTA_PATH)
        }
    )

@asset(deps=[raw_orders_bronze], group_name="silver")
def orders_silver() -> MaterializeResult:
    (PROJECT_ROOT / "data/silver").mkdir(parents=True, exist_ok=True)
    
    res = subprocess.run(
        ["dbt", "run", "--select", "stg_orders", "--profiles-dir", str(DBT_DIR)],
        cwd=str(DBT_DIR),
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        raise Exception(f"dbt run failed:\n{res.stderr}\n{res.stdout}")

    SILVER_DELTA_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(PROJECT_ROOT / "data/silver/workspace.duckdb"))
    con.execute("INSTALL delta; LOAD delta;")
    silver_arrow = con.execute("SELECT * FROM stg_orders").arrow()
    con.close()

    write_deltalake(str(SILVER_DELTA_PATH), silver_arrow, mode="overwrite")
    dt = DeltaTable(str(SILVER_DELTA_PATH))
    return MaterializeResult(metadata={"total_silver_rows": dt.to_pyarrow_table().num_rows})

@asset(deps=[orders_silver], group_name="gold")
def daily_sales_gold() -> MaterializeResult:
    res = subprocess.run(
        ["dbt", "run", "--select", "fct_daily_sales", "--profiles-dir", str(DBT_DIR)],
        cwd=str(DBT_DIR),
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        raise Exception(f"dbt run failed:\n{res.stderr}\n{res.stdout}")

    GOLD_DELTA_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(PROJECT_ROOT / "data/silver/workspace.duckdb"))
    con.execute("INSTALL delta; LOAD delta;")
    gold_arrow = con.execute("SELECT * FROM fct_daily_sales").arrow()
    con.close()

    write_deltalake(str(GOLD_DELTA_PATH), gold_arrow, mode="overwrite")
    dt = DeltaTable(str(GOLD_DELTA_PATH))
    return MaterializeResult(metadata={"gold_aggregated_rows": dt.to_pyarrow_table().num_rows})

defs = Definitions(
    assets=[raw_orders_bronze, orders_silver, daily_sales_gold],
    executor=in_process_executor
)

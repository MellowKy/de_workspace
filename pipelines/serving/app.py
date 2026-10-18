import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError
import duckdb

app = FastAPI(
    title="Medallion Data Lakehouse Serving API",
    description="Production REST API serving Gold Delta Lake aggregates",
    version="1.0.0"
)

GOLD_DELTA_PATH = PROJECT_ROOT / "data/gold/daily_sales_delta"

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "FastAPI + Delta Lake"}

@app.get("/api/v1/sales/daily")
def get_daily_sales():
    if not GOLD_DELTA_PATH.exists():
        raise HTTPException(status_code=503, detail="Gold Delta table not initialized.")

    try:
        dt = DeltaTable(str(GOLD_DELTA_PATH))
        arrow_table = dt.to_pyarrow_table()  # noqa: F841

        con = duckdb.connect()
        results = con.execute("""
            SELECT
                CAST(sales_date AS VARCHAR) AS sales_date,
                currency,
                total_orders,
                total_revenue
            FROM arrow_table
            ORDER BY sales_date DESC
        """).fetchall()
        con.close()

        sales_data = [
            {
                "sales_date": row[0],
                "currency": row[1],
                "total_orders": row[2],
                "total_revenue": row[3]
            }
            for row in results
        ]

        return {
            "status": "success",
            "record_count": len(sales_data),
            "data": sales_data
        }
    except TableNotFoundError as err:
        raise HTTPException(status_code=503, detail="Gold Delta table missing.") from err
    except (duckdb.Error, RuntimeError) as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

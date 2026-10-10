#!/usr/bin/env zsh
set -euo pipefail

SCRATCH_DIR="$HOME/de_workspace/.data_scratch"
RAW_PARTS="$SCRATCH_DIR/raw/partitions"
PROC_PARTS="$SCRATCH_DIR/processed/parquet"

# Recreate scratch directories
rm -rf "$RAW_PARTS" "$PROC_PARTS"
mkdir -p "$RAW_PARTS" "$PROC_PARTS"

echo "=================================================="
echo " Module 1: High-Throughput Parallel Stream Lab    "
echo "=================================================="

# Step 1: Ingest payload and generate partition chunks
echo "==> Step 1: Ingesting & partitioning stream files..."
curl -s "https://api.github.com/repos/duckdb/duckdb/events?per_page=100" > "$SCRATCH_DIR/raw/master_events.json"

jq -c '.[]' "$SCRATCH_DIR/raw/master_events.json" | split -l 25 - "$RAW_PARTS/part_"

echo "[OK] Created $(ls "$RAW_PARTS" | wc -l | tr -d ' ') partition files in $RAW_PARTS"

# Step 2: Dispatch parallel worker pool via xargs
echo ""
echo "==> Step 2: Dispatching worker processes across CPU cores (xargs -P 4)..."
ls "$RAW_PARTS"/part_* | xargs -I {} -P 4 ./partition_worker.sh {} "$PROC_PARTS"

echo "[OK] Conversion complete. Output Parquet files:"
ls -lh "$PROC_PARTS"/*.parquet | awk '{print "  " $9 " (" $5 ")"}'

# Step 3: Out-of-core SQL aggregation over directory glob pattern
echo ""
echo "==> Step 3: Executing SQL aggregations over Parquet lake..."
duckdb -c "
    SELECT 
      event_type,
      COUNT(*) AS total_events,
      COUNT(DISTINCT actor) AS unique_actors
    FROM read_parquet('$PROC_PARTS/*.parquet')
    GROUP BY event_type
    ORDER BY total_events DESC;
"

echo "=================================================="
echo "[SUCCESS] Modular Parallel Stream Pipeline Executed."

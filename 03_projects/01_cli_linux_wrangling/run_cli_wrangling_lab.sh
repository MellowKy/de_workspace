#!/usr/bin/env zsh
set -euo pipefail

SCRATCH_DIR="$HOME/de_workspace/.data_scratch/raw"
mkdir -p "$SCRATCH_DIR"

echo "=================================================="
echo " Module 1: Enterprise CLI Data Wrangling Lab      "
echo "=================================================="

# Step 1: Ingest live raw JSON stream into scratch buffer
RAW_FILE="$SCRATCH_DIR/github_events.json"
echo "==> Ingesting GitHub event payload..."
curl -s "https://api.github.com/repos/duckdb/duckdb/events?per_page=100" > "$RAW_FILE"

echo "[OK] Downloaded $(du -h "$RAW_FILE" | awk '{print $1}') raw JSON payload."

# Step 2: Use jq to extract, flatten, and project array into NDJSON stream
echo ""
echo "==> Step 2: Flattening JSON array via jq stream parser..."
jq -c '.[] | {id: .id, type: .type, actor: .actor.login, repo: .repo.name, created_at: .created_at}' "$RAW_FILE" \
  > "$SCRATCH_DIR/flattened_events.ndjson"

echo "[OK] Transformed $(wc -l < "$SCRATCH_DIR/flattened_events.ndjson" | tr -d ' ') JSON events to NDJSON."

# Step 3: Use sed regex substitution to split timestamps and clean schemas
echo ""
echo "==> Step 3: Sanitizing timestamps via sed stream editor..."
sed -E 's/"created_at":"([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})Z"/"event_date":"\1","event_time":"\2"/g' \
  "$SCRATCH_DIR/flattened_events.ndjson" > "$SCRATCH_DIR/sanitized_events.ndjson"

# Step 4: Use awk to extract event types and compute frequency distribution
echo ""
echo "==> Step 4: Computing frequency metrics via awk..."
awk -F'"type":"' '{print $2}' "$SCRATCH_DIR/sanitized_events.ndjson" \
  | awk -F'"' '{print $1}' \
  | sort \
  | uniq -c \
  | sort -nr \
  | awk '{printf "  %-25s : %d events\n", $2, $1}'

# Step 5: Stream NDJSON directly into DuckDB OLAP pipe via /dev/stdin
echo ""
echo "==> Step 5: Executing vectorized SQL directly on stream buffer..."
cat "$SCRATCH_DIR/sanitized_events.ndjson" \
  | duckdb -c "
    SELECT 
      actor,
      COUNT(*) AS event_count
    FROM read_json_auto('/dev/stdin')
    GROUP BY actor
    ORDER BY event_count DESC
    LIMIT 5;
  "

echo "=================================================="
echo "[SUCCESS] CLI Wrangling Pipeline executed."

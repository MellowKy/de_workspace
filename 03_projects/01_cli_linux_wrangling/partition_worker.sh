#!/usr/bin/env zsh
set -euo pipefail

input_file="$1"
output_dir="$2"
filename=$(basename "$input_file")
output_parquet="${output_dir}/${filename}.parquet"

# Stream transformation: JSON filtering -> String sanitization -> Parquet conversion
jq -c '{id: .id, type: .type, actor: .actor.login, repo: .repo.name, created_at: .created_at}' "$input_file" \
  | sed -E 's/"created_at":"([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})Z"/"event_date":"\1","event_time":"\2"/g' \
  | duckdb -c "
      COPY (
        SELECT 
          id::BIGINT AS event_id,
          type AS event_type,
          actor,
          repo,
          event_date::DATE AS event_date,
          event_time
        FROM read_json_auto('/dev/stdin')
      ) TO '$output_parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
    "

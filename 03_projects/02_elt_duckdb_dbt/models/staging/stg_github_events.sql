WITH raw_data AS (
    SELECT * 
    FROM read_parquet('{{ env_var("DATA_LAKE_PATH", "../../.data_scratch/processed/parquet") }}/*.parquet')
)

SELECT
    event_id::BIGINT AS event_id,
    event_type::VARCHAR AS event_type,
    actor_username::VARCHAR AS actor_username,
    repository_name::VARCHAR AS repository_name,
    event_date::DATE AS event_date,
    event_time::VARCHAR AS event_time
FROM raw_data
WHERE event_id IS NOT NULL

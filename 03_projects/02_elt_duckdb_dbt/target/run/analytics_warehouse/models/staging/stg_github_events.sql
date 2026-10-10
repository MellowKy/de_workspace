
  
  create view "analytics_lakehouse"."main"."stg_github_events__dbt_tmp" as (
    WITH raw_data AS (
    SELECT * 
    FROM read_parquet('../../.data_scratch/processed/parquet/*.parquet')
)

SELECT
    event_id::BIGINT AS event_id,
    event_type::VARCHAR AS event_type,
    actor::VARCHAR AS actor_username,
    repo::VARCHAR AS repository_name,
    event_date::DATE AS event_date,
    event_time::VARCHAR AS event_time
FROM raw_data
WHERE event_id IS NOT NULL
  );

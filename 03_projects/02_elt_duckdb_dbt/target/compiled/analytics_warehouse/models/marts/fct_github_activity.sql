WITH staging AS (
    SELECT * FROM "analytics_lakehouse"."main"."stg_github_events"
)

SELECT
    event_date,
    event_type,
    COUNT(DISTINCT actor_username) AS unique_contributors,
    COUNT(event_id) AS total_event_count
FROM staging
GROUP BY 1, 2
ORDER BY total_event_count DESC
WITH staging_events AS (
    SELECT *
    FROM {{ ref('stg_github_events') }}
)

SELECT
    event_date,
    event_type,
    COUNT(DISTINCT actor_username) AS unique_actors,
    COUNT(event_id) AS total_events
FROM staging_events
GROUP BY
    event_date,
    event_type
ORDER BY
    total_events DESC

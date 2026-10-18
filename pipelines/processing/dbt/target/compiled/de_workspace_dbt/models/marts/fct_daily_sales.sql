SELECT 
    CAST(timestamp AT TIME ZONE 'UTC' AS DATE) AS sales_date,
    currency,
    COUNT(DISTINCT event_id) AS total_orders,
    SUM(amount) AS total_revenue
FROM "workspace"."main"."stg_orders"
GROUP BY 1, 2
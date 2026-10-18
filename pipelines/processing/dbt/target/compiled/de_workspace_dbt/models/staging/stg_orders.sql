WITH raw_data AS (
    SELECT * FROM delta_scan('/Users/kyreesullivan/de_workspace/data/bronze/orders_delta')
)
SELECT DISTINCT ON (event_id)
    event_id,
    CAST(timestamp AS TIMESTAMPTZ) AS timestamp,
    customer_id,
    CAST(amount AS DOUBLE) AS amount,
    currency
FROM raw_data
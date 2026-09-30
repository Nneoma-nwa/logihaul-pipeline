SELECT
    TRIM(d.delivery_id) AS delivery_id,
    TRIM(d.trip_id) AS trip_id,
    TRIM(d.customer_name) AS customer_name,
    TRIM(d.delivery_address) AS delivery_address,
    d.scheduled_time,
    d.actual_delivery_time,
    LOWER(TRIM(d.status)) AS status,
    NULLIF(TRIM(d.customer_phone), '') AS customer_phone

FROM {{ source('raw', 'deliveries') }} d

WHERE NOT EXISTS (
    SELECT 1
    FROM {{ ref('stg_trips_rejected') }} r
    WHERE r.trip_id = TRIM(d.trip_id)
)

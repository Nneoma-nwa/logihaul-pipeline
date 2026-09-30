SELECT
    TRIM(cost_id) AS cost_id,
    NULLIF(TRIM(trip_id), '') AS trip_id,
    TRIM(vehicle_id) AS vehicle_id,
    LOWER(TRIM(cost_type)) AS cost_type,
    amount,
    cost_date

FROM {{ source('raw', 'operating_costs') }}
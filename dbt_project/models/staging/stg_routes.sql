SELECT
    TRIM(route_id) AS route_id,
    INITCAP(TRIM(origin_city)) AS origin_city,
    INITCAP(TRIM(destination_city)) AS destination_city,
    distance_km,
    estimated_duration_hrs

FROM {{ source('raw', 'routes') }}
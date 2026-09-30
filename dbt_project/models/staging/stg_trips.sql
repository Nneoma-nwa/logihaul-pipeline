SELECT
    TRIM(trip_id) AS trip_id,
    TRIM(vehicle_id) AS vehicle_id,
    TRIM(driver_id) AS driver_id,
    TRIM(route_id) AS route_id,
    start_time,
    end_time,
    distance_km,
    LOWER(TRIM(status)) AS status

FROM {{ source('raw', 'trips') }}

WHERE end_time >= start_time
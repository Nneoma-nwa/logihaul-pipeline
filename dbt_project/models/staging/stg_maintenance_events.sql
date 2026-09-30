SELECT
    TRIM(maintenance_id) AS maintenance_id,
    TRIM(vehicle_id) AS vehicle_id,
    maintenance_date,
    LOWER(TRIM(maintenance_type)) AS maintenance_type,
    cost,
    odometer_reading

FROM {{ source('raw', 'maintenance_events') }}
SELECT
    TRIM(vehicle_id) AS vehicle_id,
    TRIM(plate_number) AS plate_number,
    LOWER(TRIM(vehicle_type)) AS vehicle_type,
    INITCAP(TRIM(make)) AS make,
    UPPER(TRIM(model)) AS model,
    year,
    capacity_kg,
    acquisition_date,
    LOWER(TRIM(status)) AS status

FROM {{ source('raw', 'vehicles') }}
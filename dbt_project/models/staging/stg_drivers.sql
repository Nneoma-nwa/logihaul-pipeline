WITH source AS (

    SELECT *
    FROM {{ source('raw', 'drivers') }}

),

cleaned AS (

    SELECT
        TRIM(driver_id) AS driver_id,
        INITCAP(TRIM(first_name)) AS first_name,
        INITCAP(TRIM(last_name)) AS last_name,
        NULLIF(TRIM(phone_number), '') AS phone_number,
        UPPER(TRIM(license_number)) AS license_number,
        license_expiry,
        hire_date,
        INITCAP(TRIM(state_of_origin)) AS state_of_origin,
        LOWER(TRIM(status)) AS status

    FROM source

)

SELECT *
FROM cleaned
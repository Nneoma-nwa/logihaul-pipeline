{{ config(materialized='table') }}

select
    driver_id,
    first_name,
    last_name,
    phone_number,
    license_number,
    license_expiry,
    hire_date,
    state_of_origin,
    status
from {{ ref('stg_drivers') }}
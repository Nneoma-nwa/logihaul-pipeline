{{ config(materialized='table') }}

select
    vehicle_id,
    plate_number,
    vehicle_type,
    make,
    model,
    year,
    capacity_kg,
    acquisition_date,
    status
from {{ ref('stg_vehicles') }}
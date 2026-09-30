{{ config(materialized='table') }}

select
    maintenance_id,
    vehicle_id,
    vehicle_type,
    make,
    model,
    vehicle_year,
    vehicle_status,
    maintenance_date,
    maintenance_type,
    cost,
    odometer_reading,
    vehicle_age_years,
    has_negative_cost
from {{ ref('int_maintenance_analysis') }}
{{ config(materialized='table') }}

select
    route_id,
    origin_city,
    destination_city,
    distance_km,
    estimated_duration_hrs
from {{ ref('stg_routes') }}
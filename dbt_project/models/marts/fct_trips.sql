{{ config(materialized='table') }}

select
    trip_id,
    vehicle_id,
    driver_id,
    route_id,
    start_time,

    distance_km,

    vehicle_type,
    make,
    model,

    fuel_cost,
    toll_cost,
    total_trip_cost,
    cost_per_km,

    has_negative_cost

from {{ ref('int_trip_economics') }}

{{ config(materialized='table') }}

select
    vehicle_id,
    vehicle_type,
    make,
    vehicle_status,

    total_trips,
    total_distance_km,

    first_trip_date,
    last_trip_date,

    avg_trips_per_day

from {{ ref('int_fleet_activity') }}

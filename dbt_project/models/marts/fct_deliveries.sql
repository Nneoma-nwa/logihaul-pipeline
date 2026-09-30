{{ config(materialized='table') }}

select
    delivery_id,
    trip_id,

    delivery_id || '-' || trip_id as delivery_key,

    vehicle_id,
    driver_id,
    route_id,

    origin_city,
    destination_city,
    distance_km,

    scheduled_time,
    actual_delivery_time,

    delivery_status,
    delivery_duration_minutes,

    is_on_time,
    has_suspect_timestamp

from {{ ref('int_delivery_performance') }} 

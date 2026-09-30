with deliveries as (
    select * from {{ ref('stg_deliveries') }}
),

trips as (
    select * from {{ ref('stg_trips') }}
),

routes as (
    select * from {{ ref('stg_routes') }}
),

joined as (
    select
        d.delivery_id,
        d.trip_id,
        t.vehicle_id,
        t.driver_id,
        t.route_id,
        r.origin_city,
        r.destination_city,
        r.distance_km,
        d.scheduled_time,
        d.actual_delivery_time,
        d.status as delivery_status,

        extract(
            epoch from (d.actual_delivery_time - t.start_time)
        ) / 60 as delivery_duration_minutes,

        case
            when d.actual_delivery_time <= d.scheduled_time then true
            when d.actual_delivery_time > d.scheduled_time then false
            else null
        end as is_on_time,

        case
            when d.actual_delivery_time < d.scheduled_time
                - interval '15 minutes'
            then true
            else false
        end as has_suspect_timestamp

    from deliveries d

    left join trips t
        on d.trip_id = t.trip_id

    left join routes r
        on t.route_id = r.route_id
)

select * from joined
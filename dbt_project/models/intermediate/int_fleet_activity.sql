with vehicles as (
    select * from {{ ref('stg_vehicles') }}
),

trips as (
    select * from {{ ref('stg_trips') }}
),

trip_agg as (
    select
        vehicle_id,

        count(*) as total_trips,

        sum(distance_km) as total_distance_km,

        min(start_time) as first_trip_date,

        max(start_time) as last_trip_date

    from trips

    group by vehicle_id
),

joined as (
    select
        v.vehicle_id,
        v.vehicle_type,
        v.make,
        v.status as vehicle_status,

        coalesce(t.total_trips, 0) as total_trips,

        coalesce(t.total_distance_km, 0) as total_distance_km,

        t.first_trip_date,
        t.last_trip_date,

        case
            when t.total_trips > 0
                then round(
                    t.total_trips::numeric /
                    nullif(
                        extract(
                            epoch from (
                                t.last_trip_date - t.first_trip_date
                            )
                        ) / 86400,
                        0
                    ),
                    2
                )

            else 0

        end as avg_trips_per_day

    from vehicles v

    left join trip_agg t
        on v.vehicle_id = t.vehicle_id
)

select * from joined
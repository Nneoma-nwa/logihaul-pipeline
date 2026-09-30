with trips as (
    select * from {{ ref('stg_trips') }}
),

costs as (
    select * from {{ ref('stg_operating_costs') }}
),

vehicles as (
    select * from {{ ref('stg_vehicles') }}
),

cost_agg as (
    select
        trip_id,

        sum(
            case
                when cost_type = 'fuel' then amount
                else 0
            end
        ) as fuel_cost,

        sum(
            case
                when cost_type = 'toll' then amount
                else 0
            end
        ) as toll_cost,

        sum(amount) as total_trip_cost

    from costs

    where trip_id is not null

    group by trip_id
),

joined as (
    select
        t.trip_id,
        t.vehicle_id,
        t.driver_id,
        t.route_id,
        t.start_time,
        t.distance_km,

        v.vehicle_type,
        v.make,
        v.model,

        c.fuel_cost,
        c.toll_cost,
        c.total_trip_cost,

        case
            when t.distance_km > 0
                then round(c.total_trip_cost / t.distance_km, 2)
            else null
        end as cost_per_km,

        case
            when c.total_trip_cost < 0 then true
            else false
        end as has_negative_cost

    from trips t

    left join cost_agg c
        on t.trip_id = c.trip_id

    left join vehicles v
        on t.vehicle_id = v.vehicle_id
)

select * from joined
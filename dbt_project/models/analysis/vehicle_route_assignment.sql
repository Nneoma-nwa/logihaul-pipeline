with vehicle_route_stats as (
    select
        t.vehicle_id,
        t.route_id,
        r.distance_km,

        count(*) as trips_on_this_route,

        sum(t.total_trip_cost) as total_cost_on_route,

        sum(t.distance_km) as total_distance_on_route

    from analytics.fct_trips t
    join analytics.dim_route r
        on t.route_id = r.route_id

    group by
        t.vehicle_id,
        t.route_id,
        r.distance_km
),

vehicle_summary as (
    select
        vehicle_id,

        count(distinct route_id) as distinct_routes_used,

        sum(trips_on_this_route) as total_trips,

        sum(total_cost_on_route) as total_cost,

        sum(total_distance_on_route) as total_distance,

        max(trips_on_this_route) as max_trips_on_single_route,

        round(
            max(trips_on_this_route)::numeric
            / sum(trips_on_this_route),
            2
        ) as route_concentration,

        round(
            sum(total_distance_on_route)
            / nullif(sum(trips_on_this_route), 0),
            2
        ) as avg_distance_per_trip

    from vehicle_route_stats

    group by vehicle_id
)

select
    vs.*,

    round(
        vs.total_cost / nullif(vs.total_distance, 0),
        2
    ) as weighted_cost_per_km

from vehicle_summary vs
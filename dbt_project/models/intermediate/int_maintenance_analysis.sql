with maintenance as (

    select *
    from {{ ref('stg_maintenance_events') }}

),

vehicles as (

    select *
    from {{ ref('stg_vehicles') }}

),

joined as (

    select
        m.maintenance_id,
        m.vehicle_id,

        v.vehicle_type,
        v.make,
        v.model,
        v.year as vehicle_year,
        v.status as vehicle_status,

        m.maintenance_date,
        m.maintenance_type,
        m.cost,
        m.odometer_reading,

        extract(
            year from age(
                m.maintenance_date,
                v.acquisition_date
            )
        ) as vehicle_age_years,

        case
            when m.cost < 0 then true
            else false
        end as has_negative_cost

    from maintenance m

    left join vehicles v
        on m.vehicle_id = v.vehicle_id

)

select *
from joined
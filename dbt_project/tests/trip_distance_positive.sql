select
    trip_id,
    distance_km
from {{ ref('stg_trips') }}
where distance_km <= 0

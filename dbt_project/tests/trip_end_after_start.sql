select
    trip_id,
    start_time,
    end_time
from {{ ref('stg_trips') }}
where end_time < start_time

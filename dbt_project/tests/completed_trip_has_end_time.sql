select
    trip_id,
    status,
    start_time,
    end_time
from {{ ref('stg_trips') }}
where status = 'completed'
  and end_time is null

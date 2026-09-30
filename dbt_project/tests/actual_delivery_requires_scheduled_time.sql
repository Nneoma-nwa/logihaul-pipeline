select
    delivery_id,
    status,
    scheduled_time,
    actual_delivery_time
from {{ ref('stg_deliveries') }}
where actual_delivery_time is not null
  and scheduled_time is null

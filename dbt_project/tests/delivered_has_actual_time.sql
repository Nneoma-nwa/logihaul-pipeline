select
    delivery_id,
    status,
    scheduled_time,
    actual_delivery_time
from {{ ref('stg_deliveries') }}
where status = 'delivered'
  and actual_delivery_time is null

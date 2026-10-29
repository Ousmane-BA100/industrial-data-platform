select *
from {{ ref('int_production_quality') }}
where inspection_id is not null
  and inspection_date < cast(event_timestamp as date)

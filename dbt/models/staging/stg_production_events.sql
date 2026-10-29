select
    production_event_id,
    product_id,
    machine_id,
    quantity_produced,
    event_timestamp,
    shift,
    operator_id,
    status
from {{ source('raw', 'production_events') }}

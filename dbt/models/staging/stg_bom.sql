select
    bom_id,
    product_id,
    component_id,
    quantity,
    unit,
    lead_time_days
from {{ source('raw', 'bom') }}

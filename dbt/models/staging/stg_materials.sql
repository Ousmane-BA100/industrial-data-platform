select
    material_id,
    description,
    category,
    unit,
    supplier_id,
    unit_price,
    lead_time_days,
    active
from {{ source('raw', 'materials') }}

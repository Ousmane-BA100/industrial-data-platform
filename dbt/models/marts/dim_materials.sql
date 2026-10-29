select
    material_id,
    description,
    category,
    unit,
    supplier_id,
    unit_price,
    lead_time_days,
    active
from {{ ref('stg_materials') }}

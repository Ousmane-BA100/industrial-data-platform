select
    product_id,
    name,
    family,
    description,
    unit_price,
    weight_kg,
    active
from {{ source('raw', 'products') }}

select
    product_id,
    name,
    family,
    description,
    unit_price,
    weight_kg,
    active
from {{ ref('stg_products') }}

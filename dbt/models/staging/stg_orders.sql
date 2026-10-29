select
    order_id,
    supplier_id,
    material_id,
    quantity,
    unit,
    order_date,
    delivery_date,
    status,
    unit_price,
    total_amount
from {{ source('raw', 'orders') }}

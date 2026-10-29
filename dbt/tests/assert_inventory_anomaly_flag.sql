select *
from {{ ref('stg_inventory') }}
where (quantity_available < 0) <> is_negative_stock

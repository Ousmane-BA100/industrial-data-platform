select *
from {{ ref('fact_inventory_status') }}
where quantity_available < 0

select
    material_id,
    material_description,
    material_category,
    count(*) as warehouse_count,
    sum(quantity_available) as total_available_quantity,
    sum(reorder_level) as total_reorder_level,
    count(*) filter (where is_below_reorder_level) as warehouses_below_reorder_level,
    (sum(quantity_available) <= sum(reorder_level)) as needs_replenishment
from {{ ref('fact_inventory_status') }}
group by material_id, material_description, material_category

-- Stock exploitable : les stocks negatifs intentionnels restent visibles en staging,
-- mais ne sont pas proposes aux usages analytiques.
select
    i.inventory_id,
    i.material_id,
    m.description as material_description,
    m.category as material_category,
    i.warehouse,
    i.quantity_on_hand,
    i.quantity_reserved,
    i.quantity_available,
    i.reorder_level,
    i.last_movement,
    (i.quantity_available <= i.reorder_level) as is_below_reorder_level
from {{ ref('stg_inventory') }} i
left join {{ ref('stg_materials') }} m on m.material_id = i.material_id
where not i.is_negative_stock

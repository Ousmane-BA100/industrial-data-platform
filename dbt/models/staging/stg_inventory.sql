select
    inventory_id,
    material_id,
    warehouse,
    quantity_on_hand,
    quantity_reserved,
    quantity_available,
    last_movement,
    reorder_level,
    -- anomalie intentionnelle: stock negatif non filtre ici, corrige dans les marts
    case when quantity_available < 0 then true else false end as is_negative_stock
from {{ source('raw', 'inventory') }}

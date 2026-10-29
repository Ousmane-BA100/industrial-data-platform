-- BOM enrichie avec le detail du composant (materiau reel) et du produit
select
    b.bom_id,
    b.product_id,
    p.name as product_name,
    p.family as product_family,
    b.component_id,
    m.description as component_description,
    m.category as component_category,
    b.quantity,
    b.unit,
    m.unit_price as component_unit_price,
    (b.quantity * m.unit_price) as component_total_cost
from {{ ref('stg_bom') }} b
left join {{ ref('stg_products') }} p on p.product_id = b.product_id
left join {{ ref('stg_materials') }} m on m.material_id = b.component_id

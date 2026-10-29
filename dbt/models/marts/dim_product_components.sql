select
    product_id,
    product_name,
    product_family,
    component_id,
    component_description,
    component_category,
    quantity,
    unit,
    component_unit_price,
    component_total_cost
from {{ ref('int_product_components') }}
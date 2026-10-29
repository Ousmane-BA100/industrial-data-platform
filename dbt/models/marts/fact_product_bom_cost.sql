-- KPI simples: cout total des composants et nombre de composants par produit
select
    product_id,
    product_name,
    product_family,
    count(distinct component_id) as nb_components,
    sum(quantity) as total_components_qty,
    sum(component_total_cost) as total_bom_cost
from {{ ref('int_product_components') }}
group by product_id, product_name, product_family

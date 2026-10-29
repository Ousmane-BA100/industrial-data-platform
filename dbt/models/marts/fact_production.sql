-- Table de faits: une ligne par evenement de production
select
    production_event_id,
    product_id,
    machine_id,
    quantity_produced,
    event_timestamp,
    production_status
from {{ ref('int_production_quality') }}
group by
    production_event_id, product_id, machine_id,
    quantity_produced, event_timestamp, production_status

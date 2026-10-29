-- Production reliee a ses inspections qualite (0, 1 ou plusieurs par production)
select
    pe.production_event_id,
    pe.product_id,
    pe.machine_id,
    pe.quantity_produced,
    pe.event_timestamp,
    pe.status as production_status,
    qi.inspection_id,
    qi.inspection_date,
    qi.test_type,
    qi.defect_code,
    qi.status as quality_status
from {{ ref('stg_production_events') }} pe
left join {{ ref('stg_quality_inspections') }} qi
    on qi.production_event_id = pe.production_event_id

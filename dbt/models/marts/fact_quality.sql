-- Table de faits: une ligne par inspection qualite (exclut les productions non inspectees)
select
    inspection_id,
    production_event_id,
    product_id,
    inspection_date,
    test_type,
    defect_code,
    quality_status,
    production_status
from {{ ref('int_production_quality') }}
where inspection_id is not null

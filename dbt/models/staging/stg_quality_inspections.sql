select
    inspection_id,
    production_event_id,
    inspection_date,
    inspector_id,
    test_type,
    defect_code,
    status,
    comments
from {{ source('raw', 'quality_inspections') }}

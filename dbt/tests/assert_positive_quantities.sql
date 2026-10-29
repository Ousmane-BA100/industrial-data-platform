select 'bom' as source_name, bom_id as record_id
from {{ ref('stg_bom') }}
where quantity <= 0

union all

select 'production_events' as source_name, production_event_id as record_id
from {{ ref('stg_production_events') }}
where quantity_produced <= 0

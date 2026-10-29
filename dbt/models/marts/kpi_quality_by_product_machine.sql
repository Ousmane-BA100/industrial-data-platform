select
    p.product_id,
    p.machine_id,
    count(distinct p.production_event_id) as production_events,
    sum(p.quantity_produced) as quantity_produced,
    count(q.inspection_id) as inspections,
    count(*) filter (where q.quality_status = 'PASSED') as passed_inspections,
    count(*) filter (where q.quality_status = 'FAILED') as failed_inspections,
    round(
        100.0 * count(*) filter (where q.quality_status = 'PASSED')
        / nullif(count(q.inspection_id), 0),
        2
    ) as conformity_rate_pct
from {{ ref('fact_production') }} p
left join {{ ref('fact_quality') }} q
    on q.production_event_id = p.production_event_id
group by p.product_id, p.machine_id

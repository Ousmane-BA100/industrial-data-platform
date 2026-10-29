select
    defect_code,
    count(*) as inspection_count,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as defect_rate_pct
from {{ ref('fact_quality') }}
where defect_code <> 'NO_DEFECT'
group by defect_code
order by inspection_count desc, defect_code

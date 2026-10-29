select *
from {{ ref('int_production_quality') }}
where inspection_id is not null
  and (
    (quality_status = 'PASSED' and defect_code <> 'NO_DEFECT')
    or (quality_status = 'FAILED' and defect_code = 'NO_DEFECT')
    or (production_status = 'PASSED' and (quality_status <> 'PASSED' or defect_code <> 'NO_DEFECT'))
    or (production_status = 'FAILED' and (quality_status <> 'FAILED' or defect_code = 'NO_DEFECT'))
  )

select
    supplier_id,
    name,
    country,
    city,
    active,
    payment_terms
from {{ ref('stg_suppliers') }}

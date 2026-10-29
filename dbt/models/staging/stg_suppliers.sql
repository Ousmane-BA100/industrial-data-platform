select
    supplier_id,
    name,
    country,
    city,
    contact_email,
    phone,
    active,
    payment_terms,
    created_at
from {{ source('raw', 'suppliers') }}

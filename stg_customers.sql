with source as (
    select * from raw_customers
)

select
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    state,
    zipcode,
    created_at
from source
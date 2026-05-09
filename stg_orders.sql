with source as (
    select * from raw_orders
)

select
    order_id,
    customer_id,
    order_date,
    status,
    updated_at
from source
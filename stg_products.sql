with source as (
    select * from raw_products
)

select
    product_id,
    name as product_name,
    category,
    price,
    cost
from source
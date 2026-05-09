with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name,
    category,
    price,
    cost,
    (price - cost) as profit_margin
from products
{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

{% if is_incremental() %}
  {% set max_updated_at_query %}
    select max(updated_at) from {{ this }}
  {% endset %}
  
  {% set results = run_query(max_updated_at_query) %}
  
  {% if execute %}
    {% set max_updated_at = results.columns[0][0] %}
  {% else %}
    {% set max_updated_at = '1900-01-01 00:00:00' %}
  {% endif %}
{% endif %}

with orders as (
    select * from {{ ref('stg_orders') }}
),
order_items as (
    select * from {{ ref('stg_order_items') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
order_item_details as (
    select
        oi.order_id,
        count(oi.order_item_id) as total_items,
        sum(oi.quantity) as total_quantity,
        sum(oi.quantity * p.price) as order_revenue,
        sum(oi.quantity * p.cost) as order_cost
    from order_items oi
    left join products p on oi.product_id = p.product_id
    group by oi.order_id
)

select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    o.updated_at,
    coalesce(oid.total_items, 0) as total_items,
    coalesce(oid.total_quantity, 0) as total_quantity,
    coalesce(oid.order_revenue, 0.0) as order_revenue,
    coalesce(oid.order_cost, 0.0) as order_cost,
    coalesce(oid.order_revenue - oid.order_cost, 0.0) as order_profit
from orders o
left join order_item_details oid on o.order_id = oid.order_id

{% if is_incremental() and max_updated_at is not none %}

where o.updated_at >= '{{ max_updated_at }}'

{% endif %}
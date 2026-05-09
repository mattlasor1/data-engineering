import pandas as pd
from faker import Faker
import duckdb
import random
from datetime import datetime, timedelta

# Initialize Faker and seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_customers(num_customers):
    customers = []
    for _ in range(num_customers):
        customers.append({
            'customer_id': fake.unique.uuid4(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'city': fake.city(),
            'state': fake.state(),
            'zipcode': fake.zipcode(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        })
    return pd.DataFrame(customers)

def generate_products(num_products):
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Toys']
    products = []
    for _ in range(num_products):
        products.append({
            'product_id': fake.unique.uuid4(),
            'name': fake.catch_phrase(),
            'category': random.choice(categories),
            'price': round(random.uniform(10.0, 500.0), 2),
            'cost': round(random.uniform(5.0, 200.0), 2)
        })
    return pd.DataFrame(products)

def generate_orders(num_orders, customer_ids):
    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    orders = []
    for _ in range(num_orders):
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        # Simulate updated_at happening after order_date
        updated_at = order_date + timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
        orders.append({
            'order_id': fake.unique.uuid4(),
            'customer_id': random.choice(customer_ids),
            'order_date': order_date,
            'status': random.choice(statuses),
            'updated_at': updated_at
        })
    return pd.DataFrame(orders)

def generate_order_items(orders_df, product_ids):
    order_items = []
    for _, order in orders_df.iterrows():
        # 1 to 5 items per order
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            order_items.append({
                'order_item_id': fake.unique.uuid4(),
                'order_id': order['order_id'],
                'product_id': random.choice(product_ids),
                'quantity': random.randint(1, 3)
            })
    return pd.DataFrame(order_items)

def main():
    print("Generating data...")
    num_customers = 1000
    num_products = 200
    num_orders = 5000

    df_customers = generate_customers(num_customers)
    df_products = generate_products(num_products)
    df_orders = generate_orders(num_orders, df_customers['customer_id'].tolist())
    df_order_items = generate_order_items(df_orders, df_products['product_id'].tolist())

    print("Connecting to DuckDB...")
    con = duckdb.connect('ecommerce.duckdb')

    print("Loading data into DuckDB...")
    con.execute("CREATE OR REPLACE TABLE raw_customers AS SELECT * FROM df_customers")
    con.execute("CREATE OR REPLACE TABLE raw_products AS SELECT * FROM df_products")
    con.execute("CREATE OR REPLACE TABLE raw_orders AS SELECT * FROM df_orders")
    con.execute("CREATE OR REPLACE TABLE raw_order_items AS SELECT * FROM df_order_items")

    print("Data loaded successfully!")
    con.close()

if __name__ == '__main__':
    main()

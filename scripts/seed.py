import sys
import os
import random

# Add parent directory to path to import db queries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.postgres_queries import (
    delete_all_order_items, delete_all_orders, delete_all_inventory, 
    delete_all_users, insert_users_batch, insert_inventory_batch
)
from db.mongo_queries import delete_all_products, insert_many_products

# Use fixed random seed for reproducible data
random.seed(42)

def generate_product(product_id_num):
    product_id = f"P{product_id_num:04d}"
    categories = ['laptops', 'shoes', 'books', 'phones']
    category = random.choice(categories)
    price = round(random.uniform(10.0, 2000.0), 2)
    
    attributes = {}
    if category == 'laptops':
        attributes = {'ram': random.choice(['8GB', '16GB', '32GB']), 'cpu': random.choice(['i5', 'i7', 'M1', 'M2'])}
    elif category == 'shoes':
        attributes = {'size': random.randint(5, 12), 'color': random.choice(['Red', 'Blue', 'Black', 'White'])}
    elif category == 'books':
        attributes = {'author': f"Author {random.randint(1, 100)}", 'pages': random.randint(100, 1000)}
    elif category == 'phones':
        attributes = {'storage': random.choice(['64GB', '128GB', '256GB']), 'camera': random.choice(['12MP', '48MP', '108MP'])}
        
    reviews = []
    for _ in range(random.randint(0, 3)):
        reviews.append({
            'user': f"User{random.randint(1, 20)}",
            'rating': random.randint(1, 5),
            'text': "Great product!" if random.random() > 0.5 else "Not bad."
        })
        
    return {
        'product_id': product_id,
        'name': f"{category.capitalize()} Model {product_id_num}",
        'category': category,
        'price': price,
        'description': f"A fantastic {category} item.",
        'attributes': attributes,
        'reviews': reviews
    }

def main():
    print("Clearing existing data...")
    delete_all_order_items()
    delete_all_orders()
    delete_all_inventory()
    delete_all_users()
    delete_all_products()
    
    print("Generating 20 users...")
    users_data = [(f"User {i}", f"user{i}@example.com") for i in range(1, 21)]
    insert_users_batch(users_data)
    
    print("Generating 1000 products and inventory...")
    products_to_insert = []
    inventory_data = []
    
    for i in range(1, 1001):
        prod = generate_product(i)
        products_to_insert.append(prod)
        inventory_data.append((prod['product_id'], random.randint(1, 50)))
        
    insert_inventory_batch(inventory_data)
    insert_many_products(products_to_insert)
    
    print(f"Seeded {len(users_data)} users in PostgreSQL.")
    print(f"Seeded {len(inventory_data)} inventory records in PostgreSQL.")
    print(f"Seeded {len(products_to_insert)} products in MongoDB.")

if __name__ == "__main__":
    main()

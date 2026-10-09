import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    return MongoClient(os.environ.get("MONGO_URI"))

# Check mongo connection
def check_connection():
    client = get_mongo_client()
    return client.admin.command('ping')

# Delete all products
def delete_all_products():
    client = get_mongo_client()
    db = client["shop"]
    db.products.delete_many({})

# Insert multiple products
def insert_many_products(products):
    client = get_mongo_client()
    db = client["shop"]
    db.products.insert_many(products)

# Find products by category and name regex
def search_products(category=None, q=None, limit=20):
    client = get_mongo_client()
    db = client["shop"]
    filter_doc = {}
    if category: filter_doc['category'] = category
    if q: filter_doc['name'] = {'$regex': re.compile(q, re.IGNORECASE)}
    return list(db.products.find(filter_doc, {'_id': 0}).sort('price', 1).limit(limit))

# Find a single product by ID
def get_product_by_id(product_id):
    client = get_mongo_client()
    db = client["shop"]
    return db.products.find_one({'product_id': product_id}, {'_id': 0})

# Find multiple products by a list of IDs
def get_products_by_ids(product_ids):
    client = get_mongo_client()
    db = client["shop"]
    return list(db.products.find({'product_id': {'$in': product_ids}}, {'_id': 0}))

# Explain search query performance
def explain_search_performance(category):
    client = get_mongo_client()
    db = client["shop"]
    return db.products.find({"category": category}).sort("price", 1).explain()["executionStats"]

# Create an index for category and price
def create_category_price_index():
    client = get_mongo_client()
    db = client["shop"]
    db.products.create_index([("category", 1), ("price", 1)])

# Drop the category price index
def drop_category_price_index():
    client = get_mongo_client()
    db = client["shop"]
    try:
        db.products.drop_index("category_1_price_1")
    except Exception:
        pass

# Get a small sample of products
def get_sample_products(limit=5):
    client = get_mongo_client()
    db = client["shop"]
    return list(db.products.find({}, {"_id": 0}).limit(limit))

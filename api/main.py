from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from db.mongo_queries import search_products, get_product_by_id, get_products_by_ids
from db.postgres_queries import get_inventory_stock, place_order_transaction, get_orders_by_user, get_order_items, get_users
from db.chroma_queries import get_similar_product_ids

app = FastAPI()

# Store last 20 requests
request_log = []

import datetime

def log_request(endpoint: str, store: str, query_text: str):
    request_log.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint, 
        "store": store, 
        "query_text": query_text
    })
    if len(request_log) > 20:
        request_log.pop(0)

class OrderItemInput(BaseModel):
    product_id: str
    qty: int

class OrderInput(BaseModel):
    user_id: int
    items: List[OrderItemInput]

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/users")
def get_users_endpoint():
    log_request("GET /users", "Postgres", "all")
    return get_users()

@app.get("/products")
def get_products(category: Optional[str] = None, q: Optional[str] = None):
    log_request("GET /products", "Mongo", f"category={category}, q={q}")
    return search_products(category, q, 20)

@app.get("/products/{product_id}")
def get_product(product_id: str):
    log_request(f"GET /products/{product_id}", "Mongo+Postgres", f"id={product_id}")
    prod = get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock_record = get_inventory_stock(product_id)
    prod['stock'] = stock_record['stock'] if stock_record else 0
    return prod

@app.get("/products/{product_id}/similar")
def get_similar(product_id: str):
    log_request(f"GET /products/{product_id}/similar", "vector", f"product_id={product_id}")
    similar_ids = get_similar_product_ids(product_id, 5)
    if not similar_ids:
        return []
    
    products = get_products_by_ids(similar_ids)
    prod_map = {p["product_id"]: p for p in products}
    # Preserve the similarity ordering from Chroma
    return [prod_map[pid] for pid in similar_ids if pid in prod_map]

@app.post("/orders")
def create_order(order: OrderInput):
    log_request("POST /orders", "Mongo+Postgres", f"user={order.user_id}, items={len(order.items)}")
    
    enriched_items = []
    total = 0.0
    for item in order.items:
        prod = get_product_by_id(item.product_id)
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        
        enriched_items.append({
            "product_id": item.product_id,
            "qty": item.qty,
            "name": prod["name"],
            "price": prod["price"]
        })
        total += float(prod["price"]) * item.qty
        
    try:
        order_id = place_order_transaction(order.user_id, total, enriched_items)
        return {"order_id": order_id, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders")
def get_orders(user_id: int):
    log_request("GET /orders", "Postgres", f"user_id={user_id}")
    return get_orders_by_user(user_id)

@app.get("/orders/{order_id}/items")
def get_order_items_endpoint(order_id: int):
    log_request(f"GET /orders/{order_id}/items", "Postgres", f"order_id={order_id}")
    return get_order_items(order_id)

@app.get("/debug/requests")
def get_debug_requests():
    return {"requests": request_log}

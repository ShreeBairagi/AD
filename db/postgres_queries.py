import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_pg_connection():
    return psycopg2.connect(os.environ.get("POSTGRES_URI"))

# Check postgres connection
def check_connection():
    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            return cur.fetchone()

# Delete all order items
def delete_all_order_items():
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE order_items RESTART IDENTITY CASCADE;")
        conn.commit()

# Delete all orders
def delete_all_orders():
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE orders RESTART IDENTITY CASCADE;")
        conn.commit()

# Delete all inventory
def delete_all_inventory():
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE inventory CASCADE;")
        conn.commit()

# Delete all users
def delete_all_users():
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
        conn.commit()

# Get all users
def get_users():
    with get_pg_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, email FROM users ORDER BY id ASC;")
        return cur.fetchall()

# Insert multiple users
def insert_users_batch(users_data):
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.executemany("INSERT INTO users (name, email) VALUES (%s, %s);", users_data)
        conn.commit()

# Insert multiple inventory records
def insert_inventory_batch(inventory_data):
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.executemany("INSERT INTO inventory (product_id, stock) VALUES (%s, %s);", inventory_data)
        conn.commit()

# Get product stock
def get_inventory_stock(product_id):
    with get_pg_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT stock FROM inventory WHERE product_id = %s;", (product_id,))
        return cur.fetchone()

# Get orders by user ID
def get_orders_by_user(user_id):
    with get_pg_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM orders WHERE user_id = %s;", (user_id,))
        return cur.fetchall()

# Get order items by order ID
def get_order_items(order_id):
    with get_pg_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM order_items WHERE order_id = %s;", (order_id,))
        return cur.fetchall()

# Update stock directly with cursor
def _update_stock(cur, item):
    cur.execute("UPDATE inventory SET stock = stock - %s WHERE product_id = %s AND stock >= %s;", (item['qty'], item['product_id'], item['qty']))
    return cur.rowcount

# Insert order directly with cursor
def _insert_order(cur, user_id, total):
    cur.execute("INSERT INTO orders (user_id, total, status) VALUES (%s, %s, 'completed') RETURNING id;", (user_id, total))
    row = cur.fetchone()
    return row['id'] if isinstance(row, dict) else row[0]

# Insert order item directly with cursor
def _insert_order_item(cur, order_id, item):
    cur.execute("INSERT INTO order_items (order_id, product_id, product_name, price, qty) VALUES (%s, %s, %s, %s, %s);", (order_id, item['product_id'], item['name'], item['price'], item['qty']))

# Process full order transaction
def place_order_transaction(user_id, total, items):
    with get_pg_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        for item in items:
            if _update_stock(cur, item) == 0:
                conn.rollback()
                raise Exception(f"Insufficient stock for {item['product_id']}")
        order_id = _insert_order(cur, user_id, total)
        for item in items:
            _insert_order_item(cur, order_id, item)
        conn.commit()
        return order_id

# Force stock to a specific value for testing
def force_stock(product_id, stock):
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE inventory SET stock = %s WHERE product_id = %s;", (stock, product_id))
        conn.commit()

# Get a single random product ID
def get_random_product_id():
    with get_pg_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT product_id FROM inventory LIMIT 1;")
        return cur.fetchone()[0]

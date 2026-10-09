import threading
import json
import urllib.request
import sys
import os

# Add parent directory to path to import db queries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.postgres_queries import force_stock, get_random_product_id, get_inventory_stock

API_URL = "http://localhost:8000"
success_count = 0
fail_count = 0
lock = threading.Lock()

def place_order(user_id, pid):
    global success_count, fail_count
    data = {"user_id": user_id, "items": [{"product_id": pid, "qty": 1}]}
    req = urllib.request.Request(f"{API_URL}/orders", data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
        with lock:
            success_count += 1
    except Exception:
        with lock:
            fail_count += 1

def main():
    pid = get_random_product_id()
    print(f"Setting stock for {pid} to 5...")
    force_stock(pid, 5)
    
    print("Sending 20 simultaneous order requests for 1 unit each...")
    threads = []
    for i in range(20):
        t = threading.Thread(target=place_order, args=(1, pid))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    final_stock = get_inventory_stock(pid)['stock']
    print(f"Successful orders (Expected: 5): {success_count}")
    print(f"Failed orders (Expected: 15): {fail_count}")
    print(f"Final stock (Expected: 0): {final_stock}")

if __name__ == "__main__":
    main()

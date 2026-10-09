import sys
import os
import urllib.request
import urllib.parse
import json

# Add parent directory to path to import db queries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.mongo_queries import get_sample_products

API_URL = "http://localhost:8000"

def get_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception:
        return []

def main():
    samples = get_sample_products(5)
    
    print(f"{'PRODUCT NAME':<40} | {'KEYWORD RESULTS (First Word)':<40} | {'VECTOR SIMILAR RESULTS'}")
    print("-" * 115)
    
    for p in samples:
        pid = p["product_id"]
        name = p["name"]
        
        # Keyword search using the first word of the name
        first_word = name.split()[0]
        q = urllib.parse.quote(first_word)
        keyword_res = get_json(f"{API_URL}/products?q={q}")
        
        # Filter out the current product itself
        keyword_names = [k["name"] for k in keyword_res if k.get("product_id") != pid][:3]
        keyword_str = ", ".join(keyword_names) if keyword_names else "None"
        
        # Vector similar search
        vector_res = get_json(f"{API_URL}/products/{pid}/similar")
        vector_names = [v["name"] for v in vector_res][:3]
        vector_str = ", ".join(vector_names) if vector_names else "None"
        
        # Truncate strings to fit comfortably
        name_trunc = (name[:37] + "...") if len(name) > 40 else name
        kw_trunc = (keyword_str[:37] + "...") if len(keyword_str) > 40 else keyword_str
        vec_trunc = (vector_str[:37] + "...") if len(vector_str) > 40 else vector_str
        
        print(f"{name_trunc:<40} | {kw_trunc:<40} | {vec_trunc}")

if __name__ == "__main__":
    main()

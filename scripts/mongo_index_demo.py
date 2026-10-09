import sys
import os

# Add parent directory to path to import db queries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.mongo_queries import explain_search_performance, create_category_price_index, drop_category_price_index

def main():
    # Drop index if it exists for a clean test
    drop_category_price_index()

    category_to_test = "laptops"
    
    print(f"--- BEFORE CREATING INDEX ---")
    stats_before = explain_search_performance(category_to_test)
    print(f"Documents examined: {stats_before.get('totalDocsExamined', 'Unknown')}")
    print(f"Execution time (ms): {stats_before.get('executionTimeMillis', 'Unknown')}")
    
    print("\nCreating index on (category, price)...")
    create_category_price_index()
    
    print("\n--- AFTER CREATING INDEX ---")
    stats_after = explain_search_performance(category_to_test)
    print(f"Documents examined: {stats_after.get('totalDocsExamined', 'Unknown')}")
    print(f"Execution time (ms): {stats_after.get('executionTimeMillis', 'Unknown')}")

if __name__ == "__main__":
    main()

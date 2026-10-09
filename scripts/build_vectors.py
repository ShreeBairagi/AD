import os
import sys
import chromadb
from chromadb.utils import embedding_functions

# Add parent directory to path to import db queries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.mongo_queries import get_mongo_client

def main():
    client = get_mongo_client()
    db = client["shop"]
    products = list(db.products.find({}, {"_id": 0}))

    if not products:
        print("No products found in MongoDB to embed.")
        return

    chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    try:
        chroma_client.delete_collection(name="products_index")
    except Exception:
        pass
        
    collection = chroma_client.create_collection(name="products_index", embedding_function=emb_fn)

    ids = []
    documents = []
    
    for p in products:
        ids.append(p["product_id"])
        documents.append(f"{p.get('name', '')} - {p.get('description', '')}")
        
    if ids:
        collection.add(documents=documents, ids=ids)
    
    print(f"Stored {len(ids)} product embeddings in ChromaDB.")

if __name__ == "__main__":
    main()

import os
import chromadb
from chromadb.utils import embedding_functions


# This index is derived from Mongo and can be rebuilt by rerunning scripts/build_vectors.py

def get_similar_product_ids(product_id, limit=5):
    chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    try:
        collection = chroma_client.get_collection(name="products_index", embedding_function=emb_fn)
        result = collection.get(ids=[product_id], include=["embeddings"])
        if not result or not result["embeddings"]:
            return []
            
        search_res = collection.query(query_embeddings=result["embeddings"], n_results=limit + 1)
        return [pid for pid in search_res["ids"][0] if pid != product_id][:limit]
    except Exception:
        return []

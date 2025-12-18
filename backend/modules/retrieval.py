import os
from modules.clients import get_openai_client, get_pinecone_index

def get_embedding(text: str):
    client = get_openai_client()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def retrieve_context(query: str, twin_id: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    
    index = get_pinecone_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"twin_id": {"$eq": twin_id}}
    )
    
    contexts = []
    for match in results["matches"]:
        contexts.append({
            "text": match["metadata"]["text"],
            "score": match["score"],
            "source_id": match["metadata"]["source_id"]
        })
    
    return contexts

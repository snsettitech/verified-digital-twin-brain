import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_context(query: str, twin_id: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    
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

import os
from modules.clients import get_openai_client, get_pinecone_index, get_cohere_client

def get_embedding(text: str):
    client = get_openai_client()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large",
        dimensions=3072
    )
    return response.data[0].embedding

def retrieve_context(query: str, twin_id: str, top_k: int = 5):
    # Log for debugging
    print(f"Retrieving context for twin {twin_id} with query: {query}")
    query_embedding = get_embedding(query)
    
    index = get_pinecone_index()
    
    # 1. Search for verified answers first (higher priority)
    verified_results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={
            "twin_id": {"$eq": twin_id},
            "is_verified": {"$eq": True}
        }
    )
    
    # 2. Search for general document chunks (Initial retrieval - fetch more for reranking)
    initial_top_k = 20 # Fetch more to rerank
    general_results = index.query(
        vector=query_embedding,
        top_k=initial_top_k,
        include_metadata=True,
        filter={
            "twin_id": {"$eq": twin_id},
            "is_verified": {"$ne": True}
        }
    )
    
    contexts = []
    
    # Process verified matches (even lower threshold because owner intent is high)
    for match in verified_results["matches"]:
        if match["score"] > 0.25:
            contexts.append({
                "text": match["metadata"]["text"],
                "score": 1.0, # Boost verified score to 100% confidence
                "source_id": match["metadata"].get("source_id", "verified_memory"),
                "is_verified": True
            })
    
    # Process general matches
    raw_general_chunks = []
    for match in general_results["matches"]:
        if match["score"] > 0.3:
            raw_general_chunks.append({
                "text": match["metadata"]["text"],
                "score": match["score"],
                "source_id": match["metadata"].get("source_id", "unknown"),
                "is_verified": False
            })
    
    # 3. Reranking Step
    cohere_client = get_cohere_client()
    if cohere_client and raw_general_chunks:
        try:
            print(f"Reranking {len(raw_general_chunks)} chunks with Cohere...")
            # Extract texts for reranking
            documents = [c["text"] for c in raw_general_chunks]
            
            rerank_res = cohere_client.rerank(
                model="rerank-v3.5",
                query=query,
                documents=documents,
                top_n=top_k
            )
            
            # Reconstruct contexts based on reranked order
            reranked_contexts = []
            for result in rerank_res.results:
                original_chunk = raw_general_chunks[result.index]
                # Update score with rerank score (usually 0-1)
                original_chunk["score"] = result.relevance_score
                reranked_contexts.append(original_chunk)
            
            contexts.extend(reranked_contexts)
        except Exception as e:
            print(f"Error during reranking: {e}. Falling back to vector scores.")
            contexts.extend(raw_general_chunks[:top_k])
    else:
        # Fallback to initial vector search results if Cohere is not configured
        contexts.extend(raw_general_chunks[:top_k])
    
    # Deduplicate and limit
    # (Verified answers are already at the top)
    final_contexts = contexts[:top_k]
    
    print(f"Found {len(final_contexts)} relevant contexts ({len([c for c in final_contexts if c.get('is_verified')])} verified)")
    return final_contexts

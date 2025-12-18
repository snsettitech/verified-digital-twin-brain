import os
import uuid
from typing import List
from PyPDF2 import PdfReader
from modules.clients import get_openai_client, get_pinecone_index
from modules.observability import supabase

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def get_embedding(text: str):
    client = get_openai_client()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

async def ingest_source(source_id: str, twin_id: str, file_path: str, filename: str = None):
    # 0. Record source in Supabase
    if filename:
        file_size = os.path.getsize(file_path)
        supabase.table("sources").insert({
            "id": source_id,
            "twin_id": twin_id,
            "filename": filename,
            "file_size": file_size,
            "status": "processing"
        }).execute()

    # 1. Extract text
    text = extract_text_from_pdf(file_path)
    
    # 2. Chunk text
    chunks = chunk_text(text)
    
    # 3. Generate embeddings and upsert to Pinecone
    index = get_pinecone_index()
    vectors = []
    for i, chunk in enumerate(chunks):
        vector_id = str(uuid.uuid4())
        embedding = get_embedding(chunk)
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "source_id": source_id,
                "twin_id": twin_id,
                "text": chunk
            }
        })
    
    # Upsert in batches of 100
    for i in range(0, len(vectors), 100):
        index.upsert(vectors[i:i + 100])
    
    # Update status to processed
    if filename:
        supabase.table("sources").update({"status": "processed"}).eq("id", source_id).execute()

    return len(vectors)

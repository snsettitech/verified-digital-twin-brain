import os
import uuid
from typing import List
from PyPDF2 import PdfReader
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def ingest_source(source_id: str, twin_id: str, file_path: str):
    # 1. Extract text
    text = extract_text_from_pdf(file_path)
    
    # 2. Chunk text
    chunks = chunk_text(text)
    
    # 3. Generate embeddings and upsert to Pinecone
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
    
    return len(vectors)

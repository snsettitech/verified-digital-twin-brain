from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from modules.auth_guard import get_current_user, verify_owner
from modules.ingestion import ingest_source
from modules.retrieval import retrieve_context
from modules.answering import generate_answer, generate_answer_stream
from modules.escalation import create_escalation
from modules.observability import (
    log_interaction, 
    create_conversation, 
    get_conversations, 
    get_messages,
    get_sources,
    supabase
)
from modules.clients import get_pinecone_index, get_openai_client
import os
import shutil
import uuid
import json
import asyncio

app = FastAPI(title="Verified Digital Twin Brain API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    health_status = {
        "status": "online",
        "services": {
            "pinecone": "unknown",
            "openai": "unknown"
        }
    }
    
    try:
        get_pinecone_index()
        health_status["services"]["pinecone"] = "connected"
    except Exception as e:
        health_status["services"]["pinecone"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    try:
        get_openai_client().models.list()
        health_status["services"]["openai"] = "connected"
    except Exception as e:
        health_status["services"]["openai"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status

@app.post("/chat/{twin_id}")
async def chat(twin_id: str, query: str, conversation_id: str = None, user=Depends(get_current_user)):
    # 1. Retrieval
    contexts = retrieve_context(query, twin_id)
    
    # 2. Logging
    if not conversation_id:
        # Create a new conversation in Supabase
        conv = create_conversation(twin_id, user.get("user_id"))
        conversation_id = conv["id"] if conv else str(uuid.uuid4())
        
    log_interaction(conversation_id, "user", query)

    # Initial metrics from retrieval
    avg_score = sum([c['score'] for c in contexts]) / len(contexts) if contexts else 0
    citations = [c['source_id'] for c in contexts]

    async def stream_generator():
        # Send metadata first
        yield json.dumps({
            "type": "metadata", 
            "confidence_score": avg_score, 
            "citations": citations,
            "conversation_id": conversation_id
        }) + "\n"

        full_content = ""
        async for chunk in generate_answer_stream(query, contexts):
            full_content += chunk
            yield json.dumps({"type": "content", "content": chunk}) + "\n"

        # 3. Final Logging
        msg = log_interaction(
            conversation_id, 
            "assistant", 
            full_content, 
            citations, 
            avg_score
        )
        
        # 4. Escalation check
        escalated = False
        if avg_score < 0.7:
            await create_escalation(msg["id"])
            escalated = True
        
        yield json.dumps({"type": "done", "escalated": escalated}) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

@app.post("/ingest/{twin_id}")
async def ingest(twin_id: str, file: UploadFile = File(...), user=Depends(verify_owner)):
    # Save file temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    source_id = str(uuid.uuid4())
    
    try:
        num_chunks = await ingest_source(source_id, twin_id, file_path, file.filename)
        return {"status": "success", "chunks_ingested": num_chunks, "source_id": source_id}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/conversations/{twin_id}")
async def list_conversations(twin_id: str, user=Depends(get_current_user)):
    return get_conversations(twin_id)

@app.get("/conversations/{conversation_id}/messages")
async def list_messages(conversation_id: str, user=Depends(get_current_user)):
    return get_messages(conversation_id)

@app.get("/sources/{twin_id}")
async def list_sources(twin_id: str, user=Depends(get_current_user)):
    return get_sources(twin_id)

@app.get("/escalations")
async def list_escalations(user=Depends(verify_owner)):
    # Simple fetch for all escalations
    response = supabase.table("escalations").select("*, messages(*)").order("created_at", desc=True).execute()
    return response.data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

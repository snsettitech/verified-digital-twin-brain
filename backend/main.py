from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from backend.modules.auth_guard import get_current_user, verify_owner
from backend.modules.ingestion import ingest_source
from backend.modules.retrieval import retrieve_context
from backend.modules.answering import generate_answer
from backend.modules.escalation import create_escalation
from backend.modules.observability import log_interaction
import os
import shutil
import uuid

app = FastAPI(title="Verified Digital Twin Brain API")

@app.post("/chat/{twin_id}")
async def chat(twin_id: str, query: str, conversation_id: str = None, user=Depends(get_current_user)):
    # 1. Retrieval
    contexts = retrieve_context(query, twin_id)
    
    # 2. Answering
    result = generate_answer(query, contexts)
    
    # 3. Logging
    if not conversation_id:
        # Create a new conversation if not provided (simplified)
        # In real app, you'd insert into Supabase here
        conversation_id = str(uuid.uuid4())
        
    log_interaction(conversation_id, "user", query)
    msg = log_interaction(
        conversation_id, 
        "assistant", 
        result["answer"], 
        result["citations"], 
        result["confidence_score"]
    )
    
    # 4. Escalation check
    if result["confidence_score"] < 0.7:
        await create_escalation(msg["id"])
        result["escalated"] = True
    else:
        result["escalated"] = False
        
    return result

@app.post("/ingest/{twin_id}")
async def ingest(twin_id: str, file: UploadFile = File(...), user=Depends(verify_owner)):
    # Save file temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # In real app, you'd create a 'source' record in Supabase first to get source_id
    source_id = str(uuid.uuid4())
    
    try:
        num_chunks = await ingest_source(source_id, twin_id, file_path)
        return {"status": "success", "chunks_ingested": num_chunks, "source_id": source_id}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

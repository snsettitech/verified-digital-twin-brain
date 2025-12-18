from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def log_interaction(conversation_id: str, role: str, content: str, citations: list = None, confidence_score: float = None):
    data = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    }
    if citations:
        data["citations"] = citations
    if confidence_score is not None:
        data["confidence_score"] = confidence_score
        
    response = supabase.table("messages").insert(data).execute()
    return response.data[0] if response.data else None

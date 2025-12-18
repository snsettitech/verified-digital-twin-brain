from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
# Fallback to anon key if service key is placeholder or missing
if not supabase_key or "your_supabase_service_role_key" in supabase_key:
    supabase_key = os.getenv("SUPABASE_KEY")
    
supabase: Client = create_client(supabase_url, supabase_key)

def create_conversation(twin_id: str, user_id: str = None):
    data = {"twin_id": twin_id}
    if user_id:
        data["user_id"] = user_id
    response = supabase.table("conversations").insert(data).execute()
    return response.data[0] if response.data else None

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

def get_conversations(twin_id: str):
    response = supabase.table("conversations").select("*").eq("twin_id", twin_id).order("created_at", desc=True).execute()
    return response.data

def get_messages(conversation_id: str):
    response = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
    return response.data

def get_sources(twin_id: str):
    response = supabase.table("sources").select("*").eq("twin_id", twin_id).order("created_at", desc=True).execute()
    return response.data

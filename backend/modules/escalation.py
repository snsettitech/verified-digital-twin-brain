from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

async def create_escalation(message_id: str):
    response = supabase.table("escalations").insert({
        "message_id": message_id,
        "status": "open"
    }).execute()
    return response.data

async def resolve_escalation(escalation_id: str, owner_id: str, reply_content: str):
    # Add reply
    supabase.table("escalation_replies").insert({
        "escalation_id": escalation_id,
        "owner_id": owner_id,
        "content": reply_content
    }).execute()
    
    # Mark escalation as resolved
    supabase.table("escalations").update({
        "status": "resolved"
    }).eq("id", escalation_id).execute()
    
    return True

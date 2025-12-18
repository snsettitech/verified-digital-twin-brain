from modules.observability import supabase
import uuid

def setup_test_data():
    print("Setting up test data in Supabase...")
    
    # 1. Create a tenant
    tenant_id = "00000000-0000-0000-0000-000000000000"
    supabase.table("tenants").upsert({
        "id": tenant_id,
        "name": "Test Tenant"
    }).execute()
    print(f"Created/Verified tenant: {tenant_id}")
    
    # 2. Create a twin
    twin_id = "eeeed554-9180-4229-a9af-0f8dd2c69e9b" # Using the ID expected by the frontend
    supabase.table("twins").upsert({
        "id": twin_id,
        "tenant_id": tenant_id,
        "name": "Test Twin",
        "description": "Used for system verification",
        "settings": {
            "system_prompt": "You are a highly efficient and concise Digital Twin. Answer briefly."
        }
    }).execute()
    print(f"Created/Verified twin: {twin_id}")
    
    # 3. Create a user
    user_id = "00000000-0000-0000-0000-000000000001"
    supabase.table("users").upsert({
        "id": user_id,
        "tenant_id": tenant_id,
        "email": "test@example.com",
        "role": "owner"
    }).execute()
    print(f"Created/Verified user: {user_id}")
    
    return twin_id

if __name__ == "__main__":
    setup_test_data()




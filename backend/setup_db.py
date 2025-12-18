from modules.observability import supabase
import uuid

def setup_test_data():
    print("Setting up test data in Supabase...")
    
    # 1. Create a tenant
    tenant_id = str(uuid.uuid4())
    supabase.table("tenants").insert({
        "id": tenant_id,
        "name": "Test Tenant"
    }).execute()
    print(f"Created tenant: {tenant_id}")
    
    # 2. Create a twin
    twin_id = str(uuid.uuid4())
    supabase.table("twins").insert({
        "id": twin_id,
        "tenant_id": tenant_id,
        "name": "Test Twin",
        "description": "Used for system verification"
    }).execute()
    print(f"Created twin: {twin_id}")
    
    # 3. Create a user
    user_id = str(uuid.uuid4())
    supabase.table("users").insert({
        "id": user_id,
        "tenant_id": tenant_id,
        "email": "test@example.com",
        "role": "owner"
    }).execute()
    print(f"Created user: {user_id}")
    
    return twin_id

if __name__ == "__main__":
    setup_test_data()




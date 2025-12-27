
import os
import sys

# Add backend directory to path to import modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(backend_dir, "backend"))

from modules.observability import supabase

def apply_migration():
    print("Applying migration_user_activity.sql...")
    
    # SQL to add column
    sql = """
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_active_at') THEN 
            ALTER TABLE users ADD COLUMN last_active_at TIMESTAMPTZ; 
            RAISE NOTICE 'Added last_active_at column';
        ELSE 
            RAISE NOTICE 'Column last_active_at already exists';
        END IF;
    END $$;
    
    CREATE INDEX IF NOT EXISTS idx_users_last_active_at ON users(last_active_at DESC);
    """
    
    try:
        # We can't run raw SQL easily with the JS client wrapper in some modes, 
        # but supabase-py has .rpc() usually.
        # Check if we have a direct SQL execution function or if we need to use a different approach.
        # Since I don't see a 'query' method on the client usually (it's postgrest), 
        # I might need to use a workaround or assuming the user has direct access.
        # BUT, the Supabase python client DOES NOT support raw SQL execution unless you use the .rpc() to a function that runs sql.
        # LIMITATION: I cannot execute DDL from the client unless I have a specific remote procedure.
        
        # HOWEVER, I can try to use standard psycopg2 if I had the connection string, but I only have the API URL/Key.
        
        # ACTUALLY, I can't run DDL via the API client easily.
        # So I will skip the script execution and tell the user to run it.
        # But I need to modify the code to be safe if the column doesn't exist.
        
        print("MIGRATION SKIPPED: Cannot execute DDL via API client.")
        print("Please run backend/database/migrations/migration_user_activity.sql in your Supabase SQL Editor.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_migration()

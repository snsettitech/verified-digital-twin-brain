import asyncio
from main import chat
import os

async def debug_chat():
    os.environ["DEV_MODE"] = "true"
    twin_id = "eeeed554-9180-4229-a9af-0f8dd2c69e9b"
    query = "Hello, what can you do?"
    auth = "Bearer development_token"
    
    print(f"Debugging chat for twin {twin_id}...")
    try:
        # Mocking the dependency injection for test
        from modules.auth_guard import get_current_user
        user = get_current_user(auth)
        
        result = await chat(twin_id=twin_id, query=query, user=user)
        print("Success:", result)
    except Exception as e:
        import traceback
        print("Caught exception:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chat())




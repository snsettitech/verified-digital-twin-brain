
# backend/verify_langfuse.py
"""Verify Langfuse v3 SDK connectivity."""

import os
import sys
import asyncio
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Verifying Langfuse v3 configuration...")
    
    # 1. Check Env Vars
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST")
    
    logger.info(f"HOST: {host}")
    logger.info(f"PUBLIC_KEY: {public[:10]}..." if public else "PUBLIC_KEY: Missing")
    logger.info(f"SECRET_KEY: {secret[:10]}..." if secret else "SECRET_KEY: Missing")
    
    if not secret or not public:
        logger.error("❌ Missing Langfuse credentials in .env")
        return
    
    # 2. Test v3 API
    try:
        from langfuse import observe, get_client
        logger.info("✅ Langfuse v3 imports successful")
    except ImportError as e:
        logger.error(f"❌ Failed to import langfuse: {e}")
        return
    
    # 3. Create a traced function using @observe
    @observe(name="verification_test")
    async def test_traced_function():
        logger.info("Inside observed function")
        return "Trace successful"
    
    try:
        result = await test_traced_function()
        logger.info(f"✅ Observed function executed: {result}")
    except Exception as e:
        logger.error(f"❌ Observed function failed: {e}")
        return
    
    # 4. Flush to ensure events are sent
    try:
        client = get_client()
        if hasattr(client, 'flush'):
            client.flush()
            logger.info("✅ Events flushed to Langfuse")
        else:
            logger.info("ℹ️ No flush method available")
    except Exception as e:
        logger.error(f"⚠️ Flush warning: {e}")
    
    logger.info("")
    logger.info("🎉 Verification complete! Check your Langfuse dashboard for a 'verification_test' trace.")

if __name__ == "__main__":
    asyncio.run(main())

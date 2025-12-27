# backend/test_langfuse_session.py
"""Test script to generate a trace with proper user_id and session_id"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Generate a test trace with user and session info."""
    
    try:
        from langfuse import observe, get_client
        import langfuse
    except ImportError:
        logger.error("Langfuse not installed")
        return
    
    # Generate unique IDs for testing
    test_user_id = "test-user-001"
    test_session_id = "test-session-001"
    test_twin_id = "test-twin-001"
    
    logger.info(f"Creating trace with user_id={test_user_id}, session_id={test_session_id}")
    
    @observe(name="test_chat_request")
    async def simulate_chat():
        """Simulate a chat request with user/session tracking."""
        
        # Update the trace with user and session info
        # Note: release and tags may not be supported in v3 - using metadata instead
        try:
            langfuse.update_current_trace(
                user_id=test_user_id,
                session_id=test_session_id,
                metadata={
                    "twin_id": test_twin_id,
                    "release": os.getenv("LANGFUSE_RELEASE", "dev"),
                    "test": True,
                }
            )
            logger.info("✅ Trace updated with user_id and session_id")
        except Exception as e:
            logger.error(f"update_current_trace failed: {e}")
        
        # Simulate some work
        await asyncio.sleep(0.1)
        
        return {"message": "Test chat completed", "user_id": test_user_id}
    
    # Run the traced function
    result = await simulate_chat()
    logger.info(f"Result: {result}")
    
    # Flush to ensure data is sent
    client = get_client()
    if client:
        client.flush()
        logger.info("✅ Events flushed to Langfuse")
    
    logger.info("")
    logger.info("🔍 Check Langfuse dashboard:")
    logger.info(f"   - Sessions: Look for session '{test_session_id}'")
    logger.info(f"   - Users: Look for user '{test_user_id}'")
    logger.info(f"   - Traces: Look for 'test_chat_request' trace")


if __name__ == "__main__":
    asyncio.run(main())

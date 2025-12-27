# backend/test_langfuse_context.py
"""Test script using langfuse_context for proper user/session tracking"""

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
    """Test different Langfuse APIs for user/session tracking."""
    
    # Test user/session IDs
    test_user_id = "user-002"
    test_session_id = "session-002"
    
    logger.info(f"Testing Langfuse APIs with user_id={test_user_id}, session_id={test_session_id}")
    
    # Try Method 1: langfuse_context (v2 style that may work in v3)
    try:
        from langfuse.decorators import langfuse_context, observe
        logger.info("✅ langfuse.decorators import successful")
        
        @observe(name="context_test")
        async def test_with_context():
            langfuse_context.update_current_trace(
                user_id=test_user_id,
                session_id=test_session_id,
                metadata={"test": True}
            )
            logger.info("✅ langfuse_context.update_current_trace called")
            return "success"
        
        result = await test_with_context()
        logger.info(f"Method 1 (langfuse_context): {result}")
        
        # Flush
        langfuse_context.flush()
        logger.info("✅ Flushed via langfuse_context")
        
    except ImportError as e:
        logger.warning(f"langfuse.decorators import failed: {e}")
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")
    
    # Try Method 2: Direct langfuse module
    try:
        import langfuse
        from langfuse import observe as observe2
        
        @observe2(name="direct_test")
        async def test_direct():
            langfuse.update_current_trace(
                user_id=test_user_id + "-direct",
                session_id=test_session_id + "-direct"
            )
            logger.info("✅ langfuse.update_current_trace called")
            return "success"
        
        result = await test_direct()
        logger.info(f"Method 2 (langfuse module): {result}")
        
    except Exception as e:
        logger.error(f"Method 2 failed: {e}")
    
    # Try Method 3: get_client with trace
    try:
        from langfuse import get_client
        client = get_client()
        
        if hasattr(client, 'trace'):
            trace = client.trace(
                name="client_trace_test",
                user_id=test_user_id + "-client",
                session_id=test_session_id + "-client"
            )
            trace.update(metadata={"test": True})
            logger.info(f"✅ Method 3 (client.trace): Created trace {trace.id if hasattr(trace, 'id') else 'unknown'}")
        else:
            logger.warning("client.trace not available")
            
        client.flush()
        logger.info("✅ Client flushed")
        
    except Exception as e:
        logger.error(f"Method 3 failed: {e}")
    
    logger.info("")
    logger.info("🔍 Check Langfuse dashboard for:")
    logger.info(f"   - Users: '{test_user_id}', '{test_user_id}-direct', '{test_user_id}-client'")
    logger.info(f"   - Sessions: '{test_session_id}', '{test_session_id}-direct', '{test_session_id}-client'")


if __name__ == "__main__":
    asyncio.run(main())

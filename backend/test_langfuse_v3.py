# backend/test_langfuse_v3.py
"""Test Langfuse v3 user/session tracking using context manager pattern"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test using context manager pattern from Langfuse docs."""
    
    test_user_id = "user-v3-test"
    test_session_id = "session-v3-test"
    
    logger.info(f"Testing with user_id={test_user_id}, session_id={test_session_id}")
    
    try:
        from langfuse import get_client
        langfuse = get_client()
        
        logger.info(f"Langfuse client type: {type(langfuse)}")
        logger.info(f"Available methods: {[m for m in dir(langfuse) if not m.startswith('_')][:20]}")
        
        # Method: Using start_as_current_observation with update_trace
        with langfuse.start_as_current_observation(
            as_type="span",
            name="user-request-v3"
        ) as root_span:
            logger.info(f"Root span type: {type(root_span)}")
            logger.info(f"Root span methods: {[m for m in dir(root_span) if not m.startswith('_')][:15]}")
            
            # Check if update_trace exists
            if hasattr(root_span, 'update_trace'):
                logger.info("✅ update_trace method found on span")
                root_span.update_trace(
                    user_id=test_user_id,
                    session_id=test_session_id,
                    metadata={"test": True}
                )
                logger.info("✅ update_trace called")
            else:
                logger.warning("❌ update_trace not found on span")
            
            # Also set input/output
            root_span.update(
                input={"query": "Test query"},
                output={"answer": "Test answer"}
            )
        
        # Flush
        langfuse.flush()
        logger.info("✅ Flushed to Langfuse")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("")
    logger.info("🔍 Check Langfuse dashboard for:")
    logger.info(f"   - Users: '{test_user_id}'")
    logger.info(f"   - Sessions: '{test_session_id}'")
    logger.info(f"   - Traces: 'user-request-v3'")


if __name__ == "__main__":
    main()

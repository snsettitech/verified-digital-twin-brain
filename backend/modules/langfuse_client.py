# backend/modules/langfuse_client.py
"""Langfuse Tracing Client (v3 API)

Provides observability for memory extraction, graph snapshot retrieval, and agent responses.
All traces are linked by twin_id for debugging and evaluation.

Langfuse SDK v3 uses OpenTelemetry-based tracing:
- Use @observe decorator for automatic tracing
- Traces are implicitly created by the first span
- Use langfuse.update_current_trace() to add attributes
"""

import os
import logging
from typing import Optional, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Check if langfuse is available
_langfuse_available = False
_observe = None
_get_client = None

try:
    from langfuse import observe, get_client
    _langfuse_available = True
    _observe = observe
    _get_client = get_client
    logger.info("Langfuse SDK v3 loaded successfully")
except ImportError:
    logger.warning("Langfuse SDK not installed - tracing disabled")


def is_langfuse_available() -> bool:
    """Check if Langfuse is available and configured."""
    if not _langfuse_available:
        return False
    
    # Check if keys are configured
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    
    return bool(secret_key and public_key)


def trace_span(name: str, metadata: dict = None):
    """
    Decorator to trace a function using Langfuse v3 @observe.
    
    Usage:
        @trace_span("scribe_extraction")
        async def extract_memories(...):
            ...
    """
    def decorator(func: Callable):
        if not _langfuse_available:
            # No tracing, return original function
            return func
        
        # Use the @observe decorator from langfuse v3
        observed_func = _observe(name=name)(func)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await observed_func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in traced function {name}: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = observed_func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in traced function {name}: {e}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def log_trace(
    name: str,
    twin_id: str = None,
    input_data: Any = None,
    output_data: Any = None,
    metadata: dict = None,
    level: str = "DEFAULT"
):
    """
    Log a trace event manually using Langfuse v3 API.
    
    In v3, we use update_current_trace() if inside an observed context,
    otherwise log directly to the client.
    
    Args:
        name: Trace name (e.g., 'chat_response', 'memory_extraction')
        twin_id: Twin ID for grouping
        input_data: Input to the operation
        output_data: Output from the operation
        metadata: Additional context
        level: Log level (DEFAULT, DEBUG, INFO, WARNING, ERROR)
    """
    if not is_langfuse_available():
        return None
    
    try:
        import langfuse
        
        # Try to update current trace if we're in an observed context
        try:
            langfuse.update_current_trace(
                user_id=twin_id,
                metadata=metadata or {},
                input=str(input_data)[:1000] if input_data else None,
                output=str(output_data)[:1000] if output_data else None,
            )
            return "current_trace"
        except Exception:
            pass
        
        # Fallback: create a score/event on the client
        client = _get_client()
        if client:
            # Use the event API as a fallback
            client.event(
                name=name,
                metadata={
                    "twin_id": twin_id,
                    "level": level,
                    **(metadata or {})
                },
                input=str(input_data)[:1000] if input_data else None,
                output=str(output_data)[:1000] if output_data else None,
            )
            return "event"
        
        return None
    except Exception as e:
        logger.error(f"Failed to log trace: {e}")
        return None


def log_generation(
    name: str,
    twin_id: str = None,
    model: str = None,
    prompt: str = None,
    completion: str = None,
    usage: dict = None,
    metadata: dict = None
):
    """
    Log an LLM generation event.
    
    In v3, use the @observe decorator with as_type="generation" instead.
    This function provides a fallback for manual logging.
    
    Args:
        name: Generation name (e.g., 'scribe_extraction')
        twin_id: Twin ID
        model: Model name (e.g., 'gpt-4o')
        prompt: The prompt sent
        completion: The completion received
        usage: Token usage dict
        metadata: Additional context
    """
    if not is_langfuse_available():
        return None
    
    try:
        import langfuse
        
        # Try to update current observation if we're in context
        try:
            langfuse.update_current_observation(
                model=model,
                usage=usage,
                metadata={
                    "twin_id": twin_id,
                    **(metadata or {})
                }
            )
            return "current_observation"
        except Exception:
            pass
        
        return None
    except Exception as e:
        logger.error(f"Failed to log generation: {e}")
        return None


def flush():
    """Flush any pending events to Langfuse."""
    if not is_langfuse_available():
        return
    
    try:
        client = _get_client()
        if client and hasattr(client, 'flush'):
            client.flush()
    except Exception as e:
        logger.error(f"Failed to flush Langfuse: {e}")


# Convenience decorators for common operations
def trace_scribe(func):
    """Decorator for Scribe extraction functions."""
    return trace_span("scribe_extraction")(func)


def trace_graph_snapshot(func):
    """Decorator for Graph Snapshot retrieval."""
    return trace_span("graph_snapshot")(func)


def trace_agent_response(func):
    """Decorator for Agent response generation."""
    return trace_span("agent_response")(func)


# Legacy compatibility - get_langfuse returns None in v3
def get_langfuse():
    """Legacy function - returns client if available."""
    if not is_langfuse_available():
        return None
    try:
        return _get_client()
    except Exception:
        return None

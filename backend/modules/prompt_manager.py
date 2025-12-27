# backend/modules/prompt_manager.py
"""Prompt Manager for version-controlled prompts.

Provides versioned prompts for LLM calls with Langfuse tracking.
Prompts can be loaded from local files or synced with Langfuse Prompt Management.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

# Prompt directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Current prompt versions (update when changing prompts)
PROMPT_VERSIONS = {
    "chat_system": "v1.0",
    "scribe_extraction": "v1.0",
    "hyde_generator": "v1.0",
    "query_expansion": "v1.0",
    "style_analyzer": "v1.0",
}


def get_prompt(name: str, version: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a prompt by name with version info.
    
    Args:
        name: Prompt name (e.g., 'chat_system')
        version: Optional version override
    
    Returns:
        Dict with 'text', 'name', 'version' keys
    """
    version = version or PROMPT_VERSIONS.get(name, "v1.0")
    
    # Try to load from file
    prompt_file = PROMPTS_DIR / f"{name}_{version}.txt"
    if prompt_file.exists():
        text = prompt_file.read_text(encoding="utf-8")
    else:
        # Fallback to default prompts
        text = _get_default_prompt(name)
    
    return {
        "text": text,
        "name": name,
        "version": version,
    }


def update_observation_with_prompt(prompt_name: str, prompt_version: str):
    """
    Update current Langfuse observation with prompt metadata.
    
    Call this inside an @observe'd function to tag the generation.
    """
    try:
        import langfuse
        langfuse.update_current_observation(
            metadata={
                "prompt_name": prompt_name,
                "prompt_version": prompt_version,
            }
        )
    except Exception:
        pass


def _get_default_prompt(name: str) -> str:
    """Return default prompts for common operations."""
    defaults = {
        "chat_system": (
            "You are a digital twin that represents the owner's knowledge and perspective. "
            "Answer questions based on the provided context. If you don't have relevant "
            "information in your knowledge base, acknowledge this honestly."
        ),
        "scribe_extraction": (
            "You are an expert Knowledge Graph Scribe. Extract structured entities (Nodes) "
            "and relationships (Edges) from the conversation. Focus on factual claims, "
            "metrics, definitions, and proper nouns."
        ),
        "hyde_generator": (
            "You are a knowledgeable assistant. Write a brief, factual hypothetical answer "
            "to the user's question. Focus on relevant keywords and concepts."
        ),
        "query_expansion": (
            "Generate 3 search query variations based on the user's input to improve RAG "
            "retrieval. Focus on different aspects and synonyms."
        ),
        "style_analyzer": (
            "Analyze the owner's writing style from verified responses. Identify tone, "
            "vocabulary patterns, and communication preferences."
        ),
    }
    return defaults.get(name, "")


def list_prompts() -> Dict[str, str]:
    """List all available prompts with their versions."""
    return PROMPT_VERSIONS.copy()

# backend/eval/judges.py
"""LLM Judges for Online Evaluation

Provides LLM-based evaluation of chat responses for:
- Faithfulness: Does the answer match the context?
- Citation alignment: Are citations accurate?
"""

import os
import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


async def judge_faithfulness(
    answer: str,
    context: str,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Judge if the answer is faithful to the provided context.
    
    Args:
        answer: The generated answer
        context: The retrieved context
        model: Model to use for judging
    
    Returns:
        Dict with score (0.0-1.0), reasoning, and verdict
    """
    from modules.clients import get_openai_client
    
    prompt = f"""You are an expert judge evaluating answer faithfulness.

CONTEXT PROVIDED TO THE AI:
{context[:2000]}

AI'S ANSWER:
{answer}

TASK: Evaluate if the AI's answer is faithful to the context.

Criteria:
- The answer should only contain information supported by the context
- The answer should not make claims not present in the context
- The answer can paraphrase but should not distort meaning

Respond with a JSON object:
{{
  "score": <float 0.0-1.0>,
  "verdict": "faithful" | "partially_faithful" | "unfaithful",
  "reasoning": "<brief explanation>"
}}

Only respond with the JSON, no other text."""

    try:
        client = get_openai_client()
        loop = asyncio.get_event_loop()
        
        def _call():
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
        
        response = await loop.run_in_executor(None, _call)
        result = response.choices[0].message.content
        
        import json
        return json.loads(result)
        
    except Exception as e:
        logger.error(f"Faithfulness judge failed: {e}")
        return {
            "score": None,
            "verdict": "error",
            "reasoning": str(e)
        }


async def judge_citation_alignment(
    answer: str,
    citations: list,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Judge if the citations in the answer are accurate.
    
    Args:
        answer: The generated answer
        citations: List of citation objects
        model: Model to use for judging
    
    Returns:
        Dict with aligned (bool), score, and reasoning
    """
    if not citations:
        return {
            "aligned": True,
            "score": 1.0,
            "reasoning": "No citations to evaluate"
        }
    
    from modules.clients import get_openai_client
    
    citations_text = "\n".join([
        f"- {c.get('title', 'Untitled')}: {c.get('content', '')[:200]}"
        for c in citations[:5]
    ])
    
    prompt = f"""You are an expert judge evaluating citation accuracy.

AI'S ANSWER:
{answer}

CITED SOURCES:
{citations_text}

TASK: Evaluate if the citations support the claims in the answer.

Respond with a JSON object:
{{
  "aligned": <true/false>,
  "score": <float 0.0-1.0>,
  "reasoning": "<brief explanation>"
}}

Only respond with the JSON, no other text."""

    try:
        client = get_openai_client()
        loop = asyncio.get_event_loop()
        
        def _call():
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
        
        response = await loop.run_in_executor(None, _call)
        result = response.choices[0].message.content
        
        import json
        return json.loads(result)
        
    except Exception as e:
        logger.error(f"Citation judge failed: {e}")
        return {
            "aligned": None,
            "score": None,
            "reasoning": str(e)
        }


async def run_online_eval(
    trace_id: str,
    answer: str,
    context: str,
    citations: list = None,
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Run online evaluation and log scores to Langfuse.
    
    Args:
        trace_id: Langfuse trace ID
        answer: Generated answer
        context: Retrieved context
        citations: Optional citations
        threshold: Threshold for flagging
    
    Returns:
        Dict with evaluation results
    """
    # Run judges in parallel
    faithfulness_task = judge_faithfulness(answer, context)
    citation_task = judge_citation_alignment(answer, citations or [])
    
    faithfulness_result, citation_result = await asyncio.gather(
        faithfulness_task, 
        citation_task
    )
    
    # Log scores to Langfuse
    try:
        from langfuse import get_client
        client = get_client()
        
        if faithfulness_result.get("score") is not None:
            client.score(
                trace_id=trace_id,
                name="faithfulness",
                value=faithfulness_result["score"],
                comment=faithfulness_result.get("reasoning", ""),
                data_type="NUMERIC"
            )
        
        if citation_result.get("score") is not None:
            client.score(
                trace_id=trace_id,
                name="citation_alignment",
                value=citation_result["score"],
                comment=citation_result.get("reasoning", ""),
                data_type="NUMERIC"
            )
        
        # Flag for review if below threshold
        needs_review = (
            (faithfulness_result.get("score") or 1.0) < threshold or
            (citation_result.get("score") or 1.0) < threshold
        )
        
        if needs_review:
            client.score(
                trace_id=trace_id,
                name="needs_review",
                value=1,
                comment="Low confidence - flagged for manual review",
                data_type="BOOLEAN"
            )
        
        client.flush()
        
    except Exception as e:
        logger.error(f"Failed to log eval scores: {e}")
    
    return {
        "faithfulness": faithfulness_result,
        "citation_alignment": citation_result,
        "needs_review": needs_review if 'needs_review' in dir() else False
    }

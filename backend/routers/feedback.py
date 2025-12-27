# backend/routers/feedback.py
"""User Feedback Router

Allows users to provide feedback on chat responses with thumbs up/down.
Stores feedback as Langfuse scores for quality tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

router = APIRouter(tags=["feedback"])


class FeedbackReason(str, Enum):
    INCORRECT = "incorrect"
    HALLUCINATION = "hallucination"
    OFF_TOPIC = "off_topic"
    INCOMPLETE = "incomplete"
    GREAT_ANSWER = "great_answer"
    HELPFUL = "helpful"
    OTHER = "other"


class FeedbackRequest(BaseModel):
    score: Literal[-1, 1] = Field(..., description="Thumbs down (-1) or up (+1)")
    reason: FeedbackReason = Field(..., description="Reason for feedback")
    comment: Optional[str] = Field(None, max_length=500, description="Optional additional comment")
    message_id: Optional[str] = Field(None, description="Optional message ID for context")


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    trace_id: str


@router.post("/feedback/{trace_id}", response_model=FeedbackResponse)
async def submit_feedback(
    trace_id: str,
    request: FeedbackRequest
):
    """
    Submit user feedback for a chat response.
    
    Args:
        trace_id: Langfuse trace ID to associate feedback with
        request: Feedback details (score, reason, comment)
    
    Returns:
        Confirmation of feedback submission
    """
    try:
        from langfuse import get_client
        
        client = get_client()
        if not client:
            raise HTTPException(status_code=503, detail="Langfuse client not available")
        
        # Log score to Langfuse
        client.score(
            trace_id=trace_id,
            name="user_feedback",
            value=request.score,
            comment=f"{request.reason.value}: {request.comment}" if request.comment else request.reason.value,
            data_type="NUMERIC",
        )
        
        # Also log reason as separate score for filtering
        client.score(
            trace_id=trace_id,
            name="feedback_reason",
            value=1 if request.score > 0 else 0,
            comment=request.reason.value,
            data_type="CATEGORICAL",
        )
        
        client.flush()
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
            trace_id=trace_id
        )
        
    except ImportError:
        raise HTTPException(status_code=503, detail="Langfuse SDK not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/feedback/reasons")
async def get_feedback_reasons():
    """Get available feedback reason options for the UI."""
    return {
        "positive": [
            {"value": "great_answer", "label": "Great answer"},
            {"value": "helpful", "label": "Helpful"},
        ],
        "negative": [
            {"value": "incorrect", "label": "Incorrect information"},
            {"value": "hallucination", "label": "Made up facts"},
            {"value": "off_topic", "label": "Off topic"},
            {"value": "incomplete", "label": "Incomplete answer"},
            {"value": "other", "label": "Other"},
        ]
    }

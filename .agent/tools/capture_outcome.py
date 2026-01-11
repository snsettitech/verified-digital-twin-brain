"""
Capture workflow execution outcomes for pattern analysis.

Usage:
    from .agent.tools.capture_outcome import capture_outcome
    
    capture_outcome(
        workflow_type="feature_development",
        success=True,
        duration_seconds=120.5,
        errors=[],
        improvements_needed=["Better error handling guidance"],
        metadata={"feature": "new_api_endpoint"}
    )
"""
import json
from datetime import datetime
from pathlib import Path

# Get the .agent directory (parent of tools)
AGENT_DIR = Path(__file__).parent.parent
LEARNINGS_DIR = AGENT_DIR / "learnings"
OUTCOMES_FILE = LEARNINGS_DIR / "workflow_outcomes.json"


def capture_outcome(
    workflow_type: str,
    success: bool,
    duration_seconds: float,
    errors: list[str],
    improvements_needed: list[str],
    prompt_version: str = "current",
    metadata: dict = None
) -> dict:
    """
    Log workflow outcome for later analysis.
    
    Args:
        workflow_type: Type of workflow (e.g., "feature_development", "bug_fix", "code_review")
        success: Whether the workflow completed successfully
        duration_seconds: How long the workflow took
        errors: List of error messages encountered
        improvements_needed: List of improvements that would help future workflows
        prompt_version: Version of prompts used (default: "current")
        metadata: Additional metadata about the workflow
        
    Returns:
        The logged outcome dictionary
    """
    LEARNINGS_DIR.mkdir(exist_ok=True)
    
    if OUTCOMES_FILE.exists():
        try:
            outcomes = json.loads(OUTCOMES_FILE.read_text())
        except json.JSONDecodeError:
            outcomes = []
    else:
        outcomes = []
    
    outcome = {
        "timestamp": datetime.now().isoformat(),
        "workflow_type": workflow_type,
        "success": success,
        "duration_seconds": duration_seconds,
        "errors": errors,
        "improvements_needed": improvements_needed,
        "prompt_version": prompt_version,
        "metadata": metadata or {}
    }
    
    outcomes.append(outcome)
    OUTCOMES_FILE.write_text(json.dumps(outcomes, indent=2))
    
    status = "SUCCESS" if success else "FAILED"
    print(f"[OUTCOME CAPTURED] {workflow_type}: {status}")
    if errors:
        print(f"  Errors: {len(errors)}")
    if improvements_needed:
        print(f"  Improvements needed: {len(improvements_needed)}")
    
    return outcome


if __name__ == "__main__":
    # Example usage
    capture_outcome(
        workflow_type="test",
        success=True,
        duration_seconds=1.5,
        errors=[],
        improvements_needed=[],
        metadata={"test": True}
    )
    print("Test outcome captured successfully!")


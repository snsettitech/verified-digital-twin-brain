"""
Evolve prompts based on pattern analysis and recommendations.

Usage:
    python .agent/tools/evolve_prompts.py
    
    Or import and use:
    from .agent.tools.evolve_prompts import evolve_prompts_based_on_learnings
    changes = evolve_prompts_based_on_learnings()
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Get paths
AGENT_DIR = Path(__file__).parent.parent
LEARNINGS_DIR = AGENT_DIR / "learnings"
PATTERNS_FILE = LEARNINGS_DIR / "pattern_analysis.json"
EVOLUTION_LOG = AGENT_DIR.parent / "docs" / "ai" / "improvements" / "prompt_evolution_log.md"


def evolve_prompts_based_on_learnings() -> dict:
    """
    Analyze patterns and generate prompt improvement suggestions.
    
    Returns:
        Dictionary with proposed changes
    """
    if not PATTERNS_FILE.exists():
        result = {
            "error": "No pattern analysis available",
            "message": f"Run analyze_workflows.py first. No file at {PATTERNS_FILE}"
        }
        print(f"[EVOLUTION] {result['message']}")
        return result
    
    try:
        analysis = json.loads(PATTERNS_FILE.read_text())
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in pattern analysis: {e}"}
    
    recommendations = analysis.get("recommendations", [])
    
    if not recommendations:
        return {
            "message": "No recommendations to process",
            "changes_proposed": 0,
            "changes": []
        }
    
    # Filter for high and medium priority recommendations
    important_recs = [
        r for r in recommendations
        if r.get("priority") in ["high", "medium"]
    ]
    
    changes = []
    for rec in important_recs:
        # Determine which prompt file to update
        prompt_file = determine_prompt_file(rec)
        location = determine_location(rec)
        
        change = {
            "date": datetime.now().isoformat(),
            "reason": rec.get("issue", "Unknown issue"),
            "suggestion": rec.get("suggestion", ""),
            "action": rec.get("action", ""),
            "prompt_file": prompt_file,
            "location": location,
            "priority": rec.get("priority", "medium"),
            "recommendation_type": rec.get("type", "unknown")
        }
        changes.append(change)
    
    # Log evolution
    if changes:
        log_evolution(changes)
    
    result = {
        "changes_proposed": len(changes),
        "changes": changes,
        "message": f"Generated {len(changes)} prompt improvement suggestions"
    }
    
    print(f"[EVOLUTION] {result['message']}")
    if changes:
        print(f"[EVOLUTION] Changes logged to {EVOLUTION_LOG}")
        print("\n=== Suggested Changes ===")
        for i, change in enumerate(changes[:5], 1):
            print(f"{i}. [{change['priority'].upper()}] {change['reason']}")
            print(f"   → {change['prompt_file']} → {change['location']}")
    
    return result


def determine_prompt_file(recommendation: dict) -> str:
    """Determine which prompt file should be updated based on recommendation."""
    rec_type = recommendation.get("type", "")
    issue = recommendation.get("issue", "").lower()
    
    if "error_pattern" in rec_type or "error" in issue:
        return "AGENTS.md"
    elif "workflow" in issue or "command" in issue:
        return "docs/ai/commands/"
    elif "auth" in issue:
        return "docs/ops/AUTH_TROUBLESHOOTING.md"
    elif "database" in issue or "schema" in issue:
        return "docs/KNOWN_FAILURES.md"
    else:
        return "AGENTS.md"


def determine_location(recommendation: dict) -> str:
    """Determine which section of the prompt file should be updated."""
    rec_type = recommendation.get("type", "")
    action = recommendation.get("action", "").lower()
    
    if "Common AI Failure Patterns" in action:
        return "Common AI Failure Patterns section"
    elif "command card" in action:
        return "Relevant command card"
    elif "workflow" in action:
        return "Relevant workflow file"
    elif "error_pattern" in rec_type:
        return "Common AI Failure Patterns section"
    else:
        return "Appropriate section based on context"


def log_evolution(changes: list):
    """Log prompt evolution for tracking."""
    EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    if EVOLUTION_LOG.exists():
        content = EVOLUTION_LOG.read_text()
    else:
        content = "# Prompt Evolution Log\n\n"
        content += "This file tracks how prompts evolve based on workflow outcomes and pattern analysis.\n\n"
        content += "---\n\n"
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    section = f"\n## {date_str}\n\n"
    
    for change in changes:
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(change.get("priority", "medium"), "⚪")
        
        section += f"### {priority_emoji} {change['reason']}\n\n"
        section += f"**Issue:** {change['reason']}\n\n"
        section += f"**Suggestion:** {change['suggestion']}\n\n"
        section += f"**Location:** `{change['prompt_file']}` → {change['location']}\n\n"
        section += f"**Action:** {change.get('action', 'Review and implement manually')}\n\n"
        section += "---\n\n"
    
    EVOLUTION_LOG.write_text(content + section)


if __name__ == "__main__":
    result = evolve_prompts_based_on_learnings()
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    if result.get("changes_proposed", 0) == 0:
        print("No changes proposed at this time.")
    else:
        print(f"\nTotal changes proposed: {result['changes_proposed']}")
        print(f"\nReview the log at: {EVOLUTION_LOG}")
        print("\nTo apply changes:")
        print("1. Review the evolution log")
        print("2. Update the suggested prompt files manually")
        print("3. Test the updated prompts")
        print("4. Commit changes")


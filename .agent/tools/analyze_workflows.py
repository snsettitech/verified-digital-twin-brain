"""
Analyze workflow outcomes to identify patterns and improvements.

Usage:
    python .agent/tools/analyze_workflows.py
    
    Or import and use:
    from .agent.tools.analyze_workflows import analyze_patterns
    analysis = analyze_patterns(days_back=30)
"""
import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

# Get the .agent directory (parent of tools)
AGENT_DIR = Path(__file__).parent.parent
LEARNINGS_DIR = AGENT_DIR / "learnings"
OUTCOMES_FILE = LEARNINGS_DIR / "workflow_outcomes.json"
PATTERNS_FILE = LEARNINGS_DIR / "pattern_analysis.json"
SUGGESTIONS_FILE = LEARNINGS_DIR / "improvement_suggestions.md"


def analyze_patterns(days_back: int = 30) -> dict:
    """
    Analyze recent workflow outcomes for patterns.
    
    Args:
        days_back: Number of days to analyze (default: 30)
        
    Returns:
        Dictionary with analysis results
    """
    if not OUTCOMES_FILE.exists():
        result = {
            "error": "No outcomes to analyze",
            "message": f"Run capture_outcome() first. No file at {OUTCOMES_FILE}"
        }
        print(f"[ANALYSIS] {result['message']}")
        return result
    
    try:
        outcomes = json.loads(OUTCOMES_FILE.read_text())
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in outcomes file: {e}"}
    
    if not outcomes:
        return {"error": "Outcomes file is empty"}
    
    cutoff = datetime.now() - timedelta(days=days_back)
    
    recent = []
    for o in outcomes:
        try:
            timestamp = datetime.fromisoformat(o["timestamp"])
            if timestamp > cutoff:
                recent.append(o)
        except (KeyError, ValueError):
            # Skip invalid entries
            continue
    
    if not recent:
        return {
            "error": f"No outcomes in the last {days_back} days",
            "total_outcomes": len(outcomes)
        }
    
    # Analyze patterns
    error_patterns = Counter()
    improvement_themes = Counter()
    workflow_success_rates = {}
    workflow_durations = {}
    
    for outcome in recent:
        # Error patterns
        for error in outcome.get("errors", []):
            # Extract error type (first few words)
            error_words = error.split()[:3]
            error_type = " ".join(error_words)
            if error_type:
                error_patterns[error_type] += 1
        
        # Improvement themes
        for improvement in outcome.get("improvements_needed", []):
            theme_words = improvement.split()[:2]
            theme = " ".join(theme_words)
            if theme:
                improvement_themes[theme] += 1
        
        # Success rates by workflow type
        wf_type = outcome.get("workflow_type", "unknown")
        if wf_type not in workflow_success_rates:
            workflow_success_rates[wf_type] = {"success": 0, "total": 0}
            workflow_durations[wf_type] = []
        
        workflow_success_rates[wf_type]["total"] += 1
        if outcome.get("success", False):
            workflow_success_rates[wf_type]["success"] += 1
        
        # Track durations
        duration = outcome.get("duration_seconds", 0)
        if duration > 0:
            workflow_durations[wf_type].append(duration)
    
    # Calculate success rates
    success_rate_summary = {}
    for wf_type, stats in workflow_success_rates.items():
        durations = workflow_durations.get(wf_type, [])
        avg_duration = sum(durations) / len(durations) if durations else 0
        success_rate_summary[wf_type] = {
            "success_rate": stats["success"] / stats["total"] if stats["total"] > 0 else 0,
            "success": stats["success"],
            "total": stats["total"],
            "avg_duration_seconds": avg_duration
        }
    
    analysis = {
        "analysis_date": datetime.now().isoformat(),
        "period_days": days_back,
        "total_outcomes": len(recent),
        "error_patterns": dict(error_patterns.most_common(10)),
        "improvement_themes": dict(improvement_themes.most_common(10)),
        "workflow_success_rates": success_rate_summary,
        "recommendations": generate_recommendations(error_patterns, improvement_themes)
    }
    
    # Save analysis
    LEARNINGS_DIR.mkdir(exist_ok=True)
    PATTERNS_FILE.write_text(json.dumps(analysis, indent=2))
    
    # Generate human-readable suggestions
    generate_suggestions_markdown(analysis)
    
    print(f"[ANALYSIS] Analyzed {len(recent)} outcomes from last {days_back} days")
    print(f"[ANALYSIS] Results saved to {PATTERNS_FILE}")
    print(f"[ANALYSIS] Suggestions saved to {SUGGESTIONS_FILE}")
    
    return analysis


def generate_recommendations(error_patterns: Counter, improvement_themes: Counter) -> list:
    """
    Generate improvement recommendations based on patterns.
    
    Args:
        error_patterns: Counter of error patterns
        improvement_themes: Counter of improvement themes
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Top error patterns
    top_errors = error_patterns.most_common(5)
    for error_type, count in top_errors:
        recommendations.append({
            "type": "error_pattern",
            "priority": "high" if count >= 3 else "medium" if count >= 2 else "low",
            "issue": f"{error_type} (occurs {count} time{'s' if count > 1 else ''})",
            "suggestion": f"Update prompts to prevent {error_type}",
            "action": f"Add to AGENTS.md 'Common AI Failure Patterns' section"
        })
    
    # Top improvement themes
    top_improvements = improvement_themes.most_common(5)
    for theme, count in top_improvements:
        recommendations.append({
            "type": "improvement_opportunity",
            "priority": "medium",
            "issue": f"{theme} (requested {count} time{'s' if count > 1 else ''})",
            "suggestion": f"Enhance prompts with {theme} guidance",
            "action": f"Update relevant command card or workflow"
        })
    
    return recommendations


def generate_suggestions_markdown(analysis: dict):
    """Generate human-readable markdown file with suggestions."""
    recommendations = analysis.get("recommendations", [])
    
    if not recommendations:
        content = "# Improvement Suggestions\n\nNo recommendations at this time.\n"
    else:
        content = "# Improvement Suggestions\n\n"
        content += f"Generated: {analysis['analysis_date']}\n"
        content += f"Based on: {analysis['total_outcomes']} outcomes from last {analysis['period_days']} days\n\n"
        
        # Group by priority
        high_priority = [r for r in recommendations if r["priority"] == "high"]
        medium_priority = [r for r in recommendations if r["priority"] == "medium"]
        low_priority = [r for r in recommendations if r["priority"] == "low"]
        
        if high_priority:
            content += "## 🔴 High Priority\n\n"
            for rec in high_priority:
                content += f"### {rec['issue']}\n\n"
                content += f"**Suggestion:** {rec['suggestion']}\n\n"
                content += f"**Action:** {rec.get('action', 'Review and implement')}\n\n"
        
        if medium_priority:
            content += "## 🟡 Medium Priority\n\n"
            for rec in medium_priority:
                content += f"### {rec['issue']}\n\n"
                content += f"**Suggestion:** {rec['suggestion']}\n\n"
                content += f"**Action:** {rec.get('action', 'Review and implement')}\n\n"
        
        if low_priority:
            content += "## 🟢 Low Priority\n\n"
            for rec in low_priority:
                content += f"- **{rec['issue']}**: {rec['suggestion']}\n"
            content += "\n"
    
    SUGGESTIONS_FILE.write_text(content)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    analysis = analyze_patterns(days_back=days)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        sys.exit(1)
    
    print("\n=== Analysis Summary ===")
    print(f"Total outcomes: {analysis['total_outcomes']}")
    print(f"\nTop error patterns:")
    for pattern, count in list(analysis['error_patterns'].items())[:5]:
        print(f"  - {pattern}: {count}")
    
    print(f"\nTop improvement themes:")
    for theme, count in list(analysis['improvement_themes'].items())[:5]:
        print(f"  - {theme}: {count}")
    
    print(f"\nWorkflow success rates:")
    for wf_type, stats in analysis['workflow_success_rates'].items():
        print(f"  - {wf_type}: {stats['success_rate']:.1%} ({stats['success']}/{stats['total']})")
    
    print(f"\nRecommendations: {len(analysis['recommendations'])}")
    for rec in analysis['recommendations'][:3]:
        print(f"  - [{rec['priority'].upper()}] {rec['issue']}")


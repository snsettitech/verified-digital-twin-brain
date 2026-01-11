# Recursive Prompting System

> How the system improves itself through compound engineering.

## Overview

This system creates a feedback loop where workflow outcomes inform prompt improvements, which lead to better outcomes, which inform further improvements. Each iteration makes the system smarter and more effective.

## The Compound Engineering Loop

```
┌─────────────────────────────────────────────────────────┐
│            RECURSIVE PROMPTING CYCLE                     │
└─────────────────────────────────────────────────────────┘

1. EXECUTE
   │
   ├─► AI agents use current prompts
   │   ├─► AGENTS.md
   │   ├─► Command cards (docs/ai/commands/)
   │   ├─► Workflows (.agent/workflows/)
   │   └─► Troubleshooting guides
   │
   ├─► Workflow completes
   │   ├─► Success or failure
   │   ├─► Errors encountered
   │   ├─► Time taken
   │   └─► Improvements identified
   │
   ↓
   
2. CAPTURE
   │
   ├─► Outcome logged via capture_outcome()
   │   ├─► Stored in .agent/learnings/workflow_outcomes.json
   │   └─► Includes: success, errors, improvements, metadata
   │
   ↓
   
3. ANALYZE
   │
   ├─► Periodic analysis (weekly/monthly)
   │   ├─► Run analyze_workflows.py
   │   ├─► Identifies error patterns
   │   ├─► Finds improvement themes
   │   ├─► Calculates success rates
   │   └─► Generates recommendations
   │
   ├─► Results stored in:
   │   ├─► .agent/learnings/pattern_analysis.json
   │   └─► .agent/learnings/improvement_suggestions.md
   │
   ↓
   
4. EVOLVE
   │
   ├─► Run evolve_prompts.py
   │   ├─► Processes recommendations
   │   ├─► Identifies prompt files to update
   │   └─► Logs suggested changes
   │
   ├─► Changes logged to:
   │   └─► docs/ai/improvements/prompt_evolution_log.md
   │
   ├─► Manual review and update:
   │   ├─► Update AGENTS.md with new patterns
   │   ├─► Refine command cards
   │   ├─► Update workflows
   │   └─► Expand troubleshooting guides
   │
   ↓
   
5. REPEAT
   │
   └─► Improved prompts → Better outcomes → More learnings
       └─► SYSTEM COMPOUNDS ✨
```

## Usage Guide

### 1. Capturing Outcomes

After completing any workflow, capture the outcome:

```python
from datetime import datetime
import time
from .agent.tools.capture_outcome import capture_outcome

# Start timer
start_time = time.time()

# ... perform workflow ...

# Calculate duration
duration = time.time() - start_time

# Capture outcome
capture_outcome(
    workflow_type="feature_development",  # or "bug_fix", "code_review", etc.
    success=True,  # or False
    duration_seconds=duration,
    errors=[
        # List any errors encountered
        # "Missing React hooks in imports",
        # "Type mismatch in API response"
    ],
    improvements_needed=[
        # What would make this easier next time?
        # "More examples in prompts",
        # "Better error handling guidance",
        # "Clearer API documentation"
    ],
    prompt_version="current",  # Track which version of prompts was used
    metadata={
        # Additional context
        "feature": "new_api_endpoint",
        "files_changed": 5,
        "tests_added": 2,
        "complexity": "medium"
    }
)
```

### 2. Analyzing Patterns

Run periodic analysis to identify patterns:

```bash
# Analyze last 30 days (default)
python .agent/tools/analyze_workflows.py

# Analyze last 7 days
python .agent/tools/analyze_workflows.py 7

# Analyze last 90 days
python .agent/tools/analyze_workflows.py 90
```

**Output:**
- `.agent/learnings/pattern_analysis.json` - Structured analysis data
- `.agent/learnings/improvement_suggestions.md` - Human-readable suggestions

**What it analyzes:**
- Common error patterns (what errors occur most often?)
- Improvement themes (what do agents consistently request?)
- Workflow success rates (which workflows succeed/fail most?)
- Average durations (which workflows are slowest?)

### 3. Evolving Prompts

Based on analysis, generate prompt improvement suggestions:

```bash
python .agent/tools/evolve_prompts.py
```

**Output:**
- `docs/ai/improvements/prompt_evolution_log.md` - Log of suggested changes
- Console output with prioritized suggestions

**Process:**
1. Reviews pattern analysis
2. Identifies high/medium priority recommendations
3. Determines which prompt files to update
4. Logs suggested changes
5. **Manual step:** Review and apply changes

### 4. Applying Evolutions

**Manual Process (for safety):**

1. Review `docs/ai/improvements/prompt_evolution_log.md`
2. Review `.agent/learnings/improvement_suggestions.md`
3. For each suggestion:
   - Evaluate if it makes sense
   - Update the relevant prompt file
   - Test the updated prompt
   - Commit the change
4. Run analysis again to verify improvement

## Integration with Existing System

This system integrates with:

- **AGENTS.md** - Updates based on learnings (new failure patterns, conventions)
- **Command cards** (`docs/ai/commands/`) - Refined based on usage patterns
- **Troubleshooting docs** (`docs/ops/`) - Expanded with new patterns
- **Workflows** (`.agent/workflows/`) - Improved based on outcomes
- **CI/CD** - Can log workflow execution automatically
- **PR templates** - Include "improvements needed" field

## Example: Compounding Improvement

### Week 1: Initial Problem

**Outcome:**
- Error: "Missing React hooks in imports (useCallback, useEffect)"
- Frequency: High (occurs in 60% of frontend changes)

**Action:**
- Added to `AGENTS.md` as failure pattern #3
- Updated command cards with checklist
- Added to pre-commit checklist

### Week 2: First Improvement

**Outcome:**
- Error: Still occurs but less frequently (30%)
- Improvement: "Pre-commit hook would catch this automatically"

**Action:**
- Added pre-commit hook (husky + lint-staged)
- Updated prompt: "Always add ALL hooks upfront"
- Error rate drops to 10%

### Week 3: Automation

**Outcome:**
- Error: Eliminated (0%)
- Success rate: Improved
- System learned and improved itself

**Result:**
- Pattern documented
- Prevention automated
- Future agents benefit automatically

## Best Practices

### When to Capture Outcomes

**Always capture:**
- Workflow failures (to identify patterns)
- Successful workflows with improvements needed (to optimize)
- Recurring issues (to track frequency)

**Optional:**
- Simple, successful workflows (to track baseline)

### Analysis Frequency

- **Weekly**: For active development
- **Monthly**: For stable projects
- **After major changes**: To measure impact

### Prompt Evolution

- **Review suggestions**: Don't apply blindly
- **Test changes**: Verify improvements actually help
- **Track metrics**: Measure success rate changes
- **Iterate**: Continuous improvement, not perfection

## File Structure

```
.agent/
├── tools/
│   ├── capture_outcome.py      # Log workflow outcomes
│   ├── analyze_workflows.py    # Analyze patterns
│   └── evolve_prompts.py       # Generate improvements
├── learnings/
│   ├── workflow_outcomes.json  # Raw outcome data
│   ├── pattern_analysis.json   # Analysis results
│   └── improvement_suggestions.md  # Human-readable suggestions
└── workflows/
    └── with-feedback.md        # Template with feedback loop

docs/ai/
├── commands/                   # Command cards
├── improvements/
│   ├── prompt_evolution_log.md  # History of changes
│   └── workflow_metrics.md      # Performance tracking (future)
└── recursive_system.md          # This file
```

## Metrics to Track

### Workflow Metrics

- **Success rate**: % of workflows that complete successfully
- **Error frequency**: How often specific errors occur
- **Duration**: Average time per workflow type
- **Improvement requests**: What agents consistently request

### Prompt Quality Metrics

- **Error reduction**: Do errors decrease after prompt updates?
- **Success rate improvement**: Do success rates increase?
- **Duration improvement**: Do workflows get faster?
- **Agent satisfaction**: Do improvement requests decrease?

## Future Enhancements

Potential improvements:

1. **Automated prompt updates**: Auto-apply low-risk changes
2. **A/B testing**: Test prompt variations
3. **ML-based suggestions**: Use ML to predict improvements
4. **Integration with CI**: Auto-capture outcomes from CI runs
5. **Dashboard**: Visualize metrics and trends
6. **Agent feedback**: Direct feedback from AI agents

## Troubleshooting

### "No outcomes to analyze"

- Run `capture_outcome()` first
- Check that `.agent/learnings/workflow_outcomes.json` exists
- Verify JSON is valid

### "No recommendations"

- May need more outcomes (minimum 3-5 recommended)
- Increase `days_back` parameter
- Check that outcomes include errors or improvements_needed

### "Changes not applying"

- Evolution tool only suggests changes
- Manual review and update required
- See "Applying Evolutions" section above

## References

- **Compound Engineering Analysis**: `docs/COMPOUND_ENGINEERING_ANALYSIS.md`
- **Troubleshooting Methodology**: `docs/ops/TROUBLESHOOTING_METHODOLOGY.md`
- **AI Operating Manual**: `AGENTS.md`
- **Command Cards**: `docs/ai/commands/`


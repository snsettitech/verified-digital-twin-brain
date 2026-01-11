# Workflow Template with Feedback Loop

> Template for workflows that capture outcomes for recursive improvement.

## Overview

This template includes steps to capture workflow outcomes, enabling the recursive prompting system to learn and improve over time.

---

## Before Starting

### 1. Preparation

- [ ] Identify workflow type (e.g., "feature_development", "bug_fix", "code_review")
- [ ] Note start time
- [ ] Review relevant prompts:
  - [ ] `AGENTS.md` - Operating manual
  - [ ] `docs/ai/commands/` - Command cards
  - [ ] `.agent/workflows/` - Existing workflows
  - [ ] `docs/ops/` - Troubleshooting guides

### 2. Setup Tracking

```python
import time
from datetime import datetime
from .agent.tools.capture_outcome import capture_outcome

start_time = time.time()
workflow_type = "feature_development"  # Change as needed
errors_encountered = []
improvements_needed = []
```

---

## During Execution

### Follow Established Patterns

- Use prompts from `AGENTS.md` and command cards
- Follow established patterns and conventions
- Document any blockers, confusion, or ambiguities
- Note what would make this easier

### Track Issues

As you encounter issues, add them to your tracking:

```python
# When you encounter an error
errors_encountered.append("Description of error")

# When you think "this could be clearer"
improvements_needed.append("What would help: clearer guidance on X")
```

---

## After Completion

### 1. Capture Outcome

```python
from .agent.tools.capture_outcome import capture_outcome

duration = time.time() - start_time

capture_outcome(
    workflow_type=workflow_type,
    success=True,  # or False if workflow failed
    duration_seconds=duration,
    errors=errors_encountered,
    improvements_needed=improvements_needed,
    prompt_version="current",  # Or specific version if tracking
    metadata={
        # Add relevant metadata
        "files_changed": 5,
        "tests_added": 2,
        "lines_added": 150,
        "complexity": "medium",
        # Workflow-specific metadata
    }
)
```

**Required fields:**
- `workflow_type`: Type of workflow performed
- `success`: Whether workflow completed successfully
- `duration_seconds`: How long it took
- `errors`: List of errors encountered (empty list if none)
- `improvements_needed`: List of improvements that would help

**Optional metadata:**
- Files changed
- Tests added
- Lines of code
- Complexity level
- Related issue/PR numbers
- Any other relevant context

### 2. Review for Pattern Documentation

If you encountered a new pattern or issue:

- [ ] Document in relevant troubleshooting guide (`docs/ops/`)
- [ ] Update `AGENTS.md` if it's a common failure pattern
- [ ] Add to command cards if it's workflow-related
- [ ] Update workflow if it's a process issue

### 3. Suggest Prompt Improvements

If prompts could be clearer or more helpful:

- [ ] Include in `improvements_needed` when capturing outcome
- [ ] Optionally: Open issue or PR with prompt update suggestion
- [ ] Reference in PR description if prompt improvement is needed

---

## Periodic Analysis

### Weekly or Monthly

Run analysis to identify patterns:

```bash
# Analyze last 30 days
python .agent/tools/analyze_workflows.py

# Review results
cat .agent/learnings/improvement_suggestions.md
cat .agent/learnings/pattern_analysis.json
```

### Generate Evolution Suggestions

```bash
python .agent/tools/evolve_prompts.py

# Review suggestions
cat docs/ai/improvements/prompt_evolution_log.md
```

### Apply Improvements

1. Review suggested changes
2. Evaluate if they make sense
3. Update relevant prompt files
4. Test updated prompts
5. Commit improvements
6. Run analysis again to verify

---

## Workflow Types

Common workflow types to use:

- `feature_development` - New feature implementation
- `bug_fix` - Fixing bugs
- `code_review` - Reviewing code
- `refactoring` - Code refactoring
- `documentation` - Writing documentation
- `testing` - Adding/updating tests
- `deployment` - Deployment tasks
- `troubleshooting` - Debugging issues
- `migration` - Database or schema migrations
- `configuration` - Configuration changes

---

## Example: Feature Development Workflow

```python
import time
from .agent.tools.capture_outcome import capture_outcome

start_time = time.time()
errors = []
improvements = []

try:
    # ... feature development ...
    
    # If you encounter issues:
    # errors.append("Missing type hints in function signature")
    # improvements.append("More examples in command cards")
    
    success = True
except Exception as e:
    errors.append(str(e))
    success = False

duration = time.time() - start_time

capture_outcome(
    workflow_type="feature_development",
    success=success,
    duration_seconds=duration,
    errors=errors,
    improvements_needed=improvements,
    metadata={
        "feature": "new_api_endpoint",
        "files_changed": 3,
        "tests_added": 2,
        "pr_number": 123
    }
)
```

---

## Benefits

Using this template:

1. **Captures learnings** - Each workflow contributes to system improvement
2. **Identifies patterns** - Common issues become visible
3. **Enables evolution** - Prompts improve over time
4. **Tracks metrics** - Success rates and durations are measured
5. **Compounds knowledge** - System gets smarter with each workflow

---

## References

- **Recursive System Docs**: `docs/ai/recursive_system.md`
- **Capture Outcome Tool**: `.agent/tools/capture_outcome.py`
- **Analyze Workflows Tool**: `.agent/tools/analyze_workflows.py`
- **Evolve Prompts Tool**: `.agent/tools/evolve_prompts.py`
- **AI Operating Manual**: `AGENTS.md`


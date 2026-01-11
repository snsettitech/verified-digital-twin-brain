# Commit & PR: Commit Conventions and PR Description Checklist

> Reusable command card for commit messages and PR descriptions.

## Commit Message Format

### Structure

```
<type>: <short description>

<body - what and why>

<footer - optional references>
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring (no behavior change)
- `docs:` Documentation changes
- `test:` Test additions or changes
- `chore:` Maintenance (dependencies, tooling, etc.)
- `style:` Code style changes (formatting, no logic change)

### Examples

**Feature:**
```
feat: Add pre-commit hooks for frontend linting

- Install husky and lint-staged
- Configure pre-commit hook to run ESLint on staged files
- Prevent commits with lint errors

Part of repo hardening effort to prevent AI-driven regressions.
```

**Fix:**
```
fix: Correct tenant_id filter in twins query

- Changed from owner_id to tenant_id to match schema
- Fixes issue where users couldn't see their own twins

Fixes #123
```

**Refactor:**
```
refactor: Extract auth validation into separate function

- Move JWT validation logic to helper function
- Improves testability and reusability
- No behavior changes
```

**Docs:**
```
docs: Add AGENTS.md with AI operating manual

- Document architecture map and folder ownership
- List do-not-touch zones
- Capture common AI failure patterns

Reference: docs/ops/AGENT_BRIEF.md
```

**Chore:**
```
chore: Add husky and lint-staged to frontend dependencies

- Enables pre-commit hooks
- No functional changes
```

## PR Description Template

### Required Sections

#### 1. What Changed
Brief description of what this PR does.

```markdown
## What Changed

Adds pre-commit hooks to catch lint errors before push.

- Install husky and lint-staged for frontend
- Configure pre-commit hook to run ESLint
- Add AGENTS.md with AI operating manual
- Add PR template and CodeRabbit config
```

#### 2. How to Test

Step-by-step instructions for testing the changes.

```markdown
## How to Test

**Local Verification:**
1. Run `./scripts/preflight.ps1` - should pass
2. Make a lint error in a TypeScript file
3. Try to commit - should be blocked by pre-commit hook
4. Fix the error
5. Commit should succeed

**CI Verification:**
- GitHub Actions will run automatically on PR
- Check that all checks pass
```

#### 3. Risk and Rollback

Assessment of risks and how to rollback if needed.

```markdown
## Risk and Rollback

**Risk Level:** Low

**Potential Issues:**
- Pre-commit hook might block commits if lint errors exist
- Developers need to run `npm install` after checkout

**Rollback Plan:**
1. Revert PR
2. Remove husky: `cd frontend && npm uninstall husky lint-staged && rm -rf .husky`
3. Other files (AGENTS.md, PR template) are additive and can be safely removed
```

#### 4. Screenshots or Logs (if relevant)

For UI changes or complex behavior, include screenshots or logs.

```markdown
## Screenshots

Before: [screenshot]
After: [screenshot]

## Logs

[Relevant log output showing behavior]
```

### Full Example

```markdown
## What Changed

Adds comprehensive safeguards to prevent AI-driven regressions:
- Pre-commit hooks for frontend linting
- AGENTS.md with AI operating manual
- PR template with required sections
- CodeRabbit configuration

## How to Test

1. Run `./scripts/preflight.ps1` - should pass
2. Make a lint error in frontend code
3. Try to commit - should be blocked
4. Fix error - commit should succeed
5. CI will run automatically on PR

## Risk and Rollback

**Risk Level:** Low

**Potential Issues:**
- Pre-commit might block commits with lint errors
- Developers need `npm install` after checkout

**Rollback:**
- Revert PR or remove husky if needed
- Other files are additive (safe to keep or remove)

## Checklist

- [x] Ran preflight locally
- [x] All tests pass
- [x] Documentation updated
- [x] No breaking changes
- [x] Follows coding standards
```

## PR Checklist

Before submitting PR:

- [ ] Commit messages follow convention
- [ ] PR description includes all required sections
- [ ] Ran `./scripts/preflight.ps1` locally (exit code 0)
- [ ] All tests pass
- [ ] No breaking changes (or explicitly documented)
- [ ] Documentation updated if needed
- [ ] Risk assessment is honest
- [ ] Rollback plan is clear
- [ ] CI will run automatically (check workflow files)

## Reference Documents

- **Coding Standards**: `.agent/CODING_STANDARDS.md`
- **Quality Gate**: `docs/ops/QUALITY_GATE.md`
- **AI Operating Manual**: `AGENTS.md` (after this PR)


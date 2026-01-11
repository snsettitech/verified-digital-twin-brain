# Plan PR: How to Propose a PR Plan and File List

> Reusable command card for AI agents planning pull requests.

## Purpose

Before making changes, create a clear plan that lists:
- Files you will add or modify
- Exact commands to verify locally
- What will be enforced in CI
- Risk assessment

## PR Plan Format

### 1. Overview
Brief description of what the PR accomplishes.

### 2. Files to Add
```
- path/to/new/file.ext (purpose)
```

### 3. Files to Modify
```
- path/to/existing/file.ext (what changes)
```

### 4. Verification Commands

**Local Verification:**
```bash
# Commands to run locally to verify changes
./scripts/preflight.ps1  # or preflight.sh
# Additional specific commands
```

**CI Verification:**
- GitHub Actions will automatically run (`.github/workflows/lint.yml`)
- List any special checks needed

### 5. Risk Assessment

**Risk Level**: Low / Medium / High

**Potential Issues**:
- List potential breaking changes
- Areas that need careful testing
- Dependencies that might be affected

**Rollback Plan**:
- How to revert if issues arise
- Which files can be safely reverted

### 6. Testing Strategy

**Manual Testing**:
- Steps to manually verify functionality
- User flows to test

**Automated Testing**:
- Existing tests that should pass
- New tests needed (if any)

## Example Plan

### Overview
Add pre-commit hooks for frontend to catch lint errors before push.

### Files to Add
- `frontend/.husky/pre-commit` (runs lint-staged)
- `.husky/install.mjs` (husky setup)

### Files to Modify
- `frontend/package.json` (add husky, lint-staged dependencies)

### Verification Commands

**Local:**
```bash
cd frontend
npm install
git commit  # Should trigger pre-commit hook
./scripts/preflight.ps1  # Should pass
```

**CI:**
- GitHub Actions will run lint and build checks

### Risk Assessment

**Risk Level**: Low

**Potential Issues**:
- Pre-commit hook might block commits if lint errors exist
- Developers need to run `npm install` after checkout

**Rollback Plan**:
- Remove husky: `cd frontend && npm uninstall husky lint-staged`
- Remove `.husky/` directory

### Testing Strategy

**Manual Testing**:
1. Make a lint error (missing semicolon)
2. Try to commit - should be blocked
3. Fix error
4. Commit should succeed

**Automated Testing**:
- Existing lint tests should pass
- No new tests needed (pre-commit is tooling only)

## Checklist

Before creating PR:
- [ ] Plan includes all files to be modified
- [ ] Verification commands are specified
- [ ] Risk assessment is honest
- [ ] Rollback plan is clear
- [ ] Testing strategy is defined
- [ ] Dependencies are minimal (follow non-negotiables)


# ai-powertools Branch Reconciliation Guide

Generated: 2026-02-28  
Issue: `main` and `master` branches diverged

---

## Divergence Analysis

### Commit on `main` (not in `master`)
- **SHA**: `45bc936`
- **Date**: 2026-02-21
- **Message**: `feat(security): add prompt safety helpers to prevent secret leakage`
- **Files added**:
  - `src/powertools/security/__init__.py` (15 lines)
  - `src/powertools/security/prompts.py` (114 lines)

### Commit on `master` (not in `main`)
- **SHA**: `a3b322e`
- **Date**: 2026-02-21
- **PR**: #4
- **Message**: `Add Model Intelligence Framework: discovery, benchmarking, tiering, and tier-aware routing`
- **Files added**:
  - `src/powertools/model_registry/__init__.py` (36 lines)
  - `src/powertools/model_registry/benchmark.py` (99 lines)
  - `src/powertools/model_registry/discover.py` (84 lines)
  - `src/powertools/model_registry/models.py` (74 lines)
  - `src/powertools/model_registry/registry.py` (214 lines)
  - `src/powertools/model_registry/tier.py` (66 lines)
  - `tests/unit/model_registry/test_model_registry.py` (332 lines)
- **Files modified**:
  - `src/powertools/router/llm_router/router.py` (+42/-5)

### Assessment

✅ **Non-overlapping changes** - no file conflicts expected  
✅ **Both features are valuable** - merge recommended  
✅ **master is more complete** (has merged PR, more files) - use as base

---

## Recommended Reconciliation Path

**Strategy**: Merge `main` into `master`, then delete `main` and keep `master` as default.

### Step 1: Clone and verify (if not already local)

```bash
cd ~/projects
# If not already cloned:
# git clone git@github.com:zebadee2kk/ai-powertools.git
cd ai-powertools

# Verify current state
git fetch --all
git log --oneline --graph --all -10
```

### Step 2: Merge main into master

```bash
# Checkout master
git checkout master
git pull origin master

# Merge main into master
git merge origin/main -m "Merge security features from main branch

Brings in prompt safety helpers (45bc936) to prevent secret leakage.
This reconciles the main/master divergence."

# Verify merge success
git log --oneline -5
git status
```

### Step 3: Push merged master

```bash
# Push the reconciled master
git push origin master
```

### Step 4: Delete main branch remotely

```bash
# Create backup first (safety)
SHA=$(gh api repos/zebadee2kk/ai-powertools/branches/main --jq '.commit.sha')
gh api -X POST repos/zebadee2kk/ai-powertools/git/refs \
  -f ref="refs/heads/backup/main-diverged" \
  -f sha="$SHA"

# Verify backup
gh api repos/zebadee2kk/ai-powertools/branches/backup/main-diverged --jq '.name'

# Delete main
gh api -X DELETE repos/zebadee2kk/ai-powertools/git/refs/heads/main

# Verify deletion
gh api repos/zebadee2kk/ai-powertools/branches --jq '.[].name'
```

### Step 5: Clean up local tracking

```bash
cd ~/projects/ai-powertools
git fetch --prune
git branch -a
```

---

## Alternative: Keep main as default (if preferred)

If you prefer `main` as the default branch name (modern convention):

```bash
# Checkout main
git checkout main
git pull origin main

# Merge master into main
git merge origin/master -m "Merge model intelligence framework from master

Brings in model discovery, benchmarking, tiering (a3b322e) from PR #4.
This reconciles the main/master divergence."

# Push
git push origin main

# Then change default branch in GitHub UI
# Settings → Branches → Default branch → Switch to main

# After changing default, delete master:
gh api -X DELETE repos/zebadee2kk/ai-powertools/git/refs/heads/master
```

---

## Verification Commands

After reconciliation, verify everything is intact:

```bash
cd ~/projects/ai-powertools
git checkout master  # or main, depending on choice

# Check both feature sets exist
ls -la src/powertools/security/
ls -la src/powertools/model_registry/

# Run tests if available
# pytest tests/

# Verify commit history includes both
git log --oneline --all -20
```

---

## Expected Outcome

- ✅ Single unified branch (`master` or `main`) containing both features
- ✅ Backup branch (`backup/main-diverged` or `backup/master-diverged`) preserves history
- ✅ No conflicts (features touch different files)
- ✅ Clean branch list on remote

---

## Rollback (if something goes wrong)

```bash
# Restore from backup
gh api repos/zebadee2kk/ai-powertools/branches/backup/main-diverged --jq '.commit.sha' | \
  xargs -I {} gh api -X POST repos/zebadee2kk/ai-powertools/git/refs \
    -f ref="refs/heads/main" \
    -f sha={}
```

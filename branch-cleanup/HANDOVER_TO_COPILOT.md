# 🤖 Handover to VS Code Copilot

Generated: 2026-02-28 13:30 GMT
From: Perplexity AI Analysis
To: VS Code Copilot Execution

---

## Context for Copilot

This is a branch cleanup project for a developer who:
- Works on Windows laptop with WSL Ubuntu
- Has 16 GitHub repositories in portfolio
- Uses AI assistants heavily (Claude, Codex, Copilot) creating many feature branches
- Has 30+ branches across repositories that need cleanup
- Correctly identified risk of uncommitted local changes
- Prefers cautious, step-by-step approach

## Current State

Perplexity AI has:
1. ✅ Analyzed all repository branches
2. ✅ Identified 5 safe-to-delete merged branches (control-tower)
3. ✅ Identified 2 repos with dual default branches (main/master)
4. ✅ Created safety protocol for protecting local changes
5. ✅ Generated audit scripts and cleanup scripts
6. ✅ Added all files to portfolio-management repo

## Your Mission (VS Code Copilot)

Help the user safely execute the branch cleanup by:
1. Running the audit script on their Windows laptop
2. Reviewing audit output together
3. Handling any uncommitted changes or unpushed commits
4. Executing safe cleanup with backups
5. Verifying no data loss

---

## Phase 1: Initial Setup (WITH USER)

### Task 1.1: Verify Local Repository Clones

Help user identify which repos they have locally:

```bash
# In WSL Ubuntu terminal:
cd ~
find . -name ".git" -type d 2>/dev/null | grep -E "(control-tower|ai-cost-tracker|kynee|portfolio-management|ai-powertools)" | sed 's/\.git$//' | sort
```

Expected: User will have some or all of these repos cloned.

### Task 1.2: Clone portfolio-management if Needed

```bash
# If not already cloned:
cd ~/projects  # or user's preferred location
git clone git@github.com:zebadee2kk/portfolio-management.git
cd portfolio-management

# Verify branch-cleanup directory exists:
ls -la branch-cleanup/
```

---

## Phase 2: Run Safety Audit (CRITICAL)

### Task 2.1: Create Audit Script

The audit script should already be in `branch-cleanup/audit-local-branches.sh`.
If not, help user create it:

```bash
#!/bin/bash
# audit-local-branches.sh
# Run this in each repository directory

REPO_DIR=$(pwd)
REPO_NAME=$(basename "$REPO_DIR")
OUTPUT_FILE="$HOME/branch-audit-$REPO_NAME-$(hostname)-$(date +%Y%m%d-%H%M%S).txt"

echo "==================================================================" | tee "$OUTPUT_FILE"
echo "LOCAL BRANCH AUDIT: $REPO_NAME on $(hostname)" | tee -a "$OUTPUT_FILE"
echo "Date: $(date)" | tee -a "$OUTPUT_FILE"
echo "==================================================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 1. List all local branches
echo "📌 ALL LOCAL BRANCHES:" | tee -a "$OUTPUT_FILE"
git branch -v | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 2. Check for uncommitted changes
echo "⚠️  UNCOMMITTED CHANGES:" | tee -a "$OUTPUT_FILE"
if git status --short | grep -q .; then
  git status --short | tee -a "$OUTPUT_FILE"
  echo "" | tee -a "$OUTPUT_FILE"
  echo "❌ WARNING: You have uncommitted changes!" | tee -a "$OUTPUT_FILE"
else
  echo "✅ Working directory clean" | tee -a "$OUTPUT_FILE"
fi
echo "" | tee -a "$OUTPUT_FILE"

# 3. Check for unpushed commits on current branch
echo "📤 UNPUSHED COMMITS ON CURRENT BRANCH:" | tee -a "$OUTPUT_FILE"
CURRENT_BRANCH=$(git branch --show-current)
echo "  Current branch: $CURRENT_BRANCH" | tee -a "$OUTPUT_FILE"

TRACKING=$(git rev-parse --abbrev-ref "$CURRENT_BRANCH@{upstream}" 2>/dev/null)
if [ -z "$TRACKING" ]; then
  echo "  ⚠️  No upstream tracking branch set" | tee -a "$OUTPUT_FILE"
else
  UNPUSHED=$(git log --oneline "$TRACKING..$CURRENT_BRANCH" 2>/dev/null | wc -l)
  if [ "$UNPUSHED" -gt 0 ]; then
    echo "  ❌ WARNING: $UNPUSHED commits not pushed!" | tee -a "$OUTPUT_FILE"
    git log --oneline "$TRACKING..$CURRENT_BRANCH" | tee -a "$OUTPUT_FILE"
  else
    echo "  ✅ All commits pushed" | tee -a "$OUTPUT_FILE"
  fi
fi
echo "" | tee -a "$OUTPUT_FILE"

# 4. Check for stashes
echo "💾 STASHED CHANGES:" | tee -a "$OUTPUT_FILE"
if git stash list | grep -q .; then
  git stash list | tee -a "$OUTPUT_FILE"
  echo "  ⚠️  WARNING: You have stashed changes!" | tee -a "$OUTPUT_FILE"
else
  echo "  ✅ No stashes" | tee -a "$OUTPUT_FILE"
fi
echo "" | tee -a "$OUTPUT_FILE"

# 5. Summary
echo "==================================================================" | tee -a "$OUTPUT_FILE"
echo "SUMMARY:" | tee -a "$OUTPUT_FILE"
echo "  Total local branches: $(git branch | wc -l)" | tee -a "$OUTPUT_FILE"
echo "  Uncommitted files: $(git status --short | wc -l)" | tee -a "$OUTPUT_FILE"
echo "  Stashes: $(git stash list | wc -l)" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"
echo "✅ Audit complete. Output saved to: $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"
echo "==================================================================" | tee -a "$OUTPUT_FILE"
```

### Task 2.2: Run Audit on All Local Repos

Help user run this systematically:

```bash
cd ~/projects  # or wherever repos are

# Make audit script executable
chmod +x portfolio-management/branch-cleanup/audit-local-branches.sh

# Run on each repo
for repo in control-tower ai-cost-tracker kynee portfolio-management ai-powertools; do
  if [ -d "$repo" ]; then
    echo "======================================"
    echo "Auditing: $repo"
    echo "======================================"
    cd "$repo"
    bash ../portfolio-management/branch-cleanup/audit-local-branches.sh
    echo ""
    echo "Audit saved. Press Enter to continue to next repo..."
    read
    cd ..
  else
    echo "Skipping $repo (not found locally)"
  fi
done

echo ""
echo "All audits complete. Review files in ~/branch-audit-*"
ls -lh ~/branch-audit-*
```

### Task 2.3: Review Audit Results WITH USER

**CRITICAL**: Stop and review each audit file with the user.

Help them identify:
```bash
# Show all warnings across all audits:
grep -h "WARNING\|❌" ~/branch-audit-*.txt

# If any warnings found:
echo "⚠️  STOP! You have uncommitted/unpushed work."
echo "Let's review each case together."

# If no warnings:
echo "✅ All repos are clean! Safe to proceed with cleanup."
```

---

## Phase 3: Handle Any Issues Found

### If Uncommitted Changes Found:

```bash
# User decides for each repo:
cd ~/projects/REPO_WITH_CHANGES

# Option 1: Commit them
git status
git add .
git commit -m "WIP: Saving work before branch cleanup"
git push

# Option 2: Stash them
git stash save "Before cleanup - $(date +%Y-%m-%d)"

# Option 3: Discard (confirm with user first!)
# git restore .  # DANGEROUS
```

### If Unpushed Commits Found:

```bash
cd ~/projects/REPO_WITH_UNPUSHED

# Push them:
git push

# Or create backup branch:
git branch backup/$(git branch --show-current)
git push origin backup/$(git branch --show-current)
```

---

## Phase 4: Execute Safe Cleanup

### Task 4.1: Test Cleanup on ONE Branch

Start with control-tower's `docs-phase-2-5-handoff` (merged PR #41):

```bash
REPO="control-tower"
BRANCH="docs-phase-2-5-handoff"

echo "Testing safe deletion on $REPO/$BRANCH"

# 1. Verify it's merged
gh pr view 41 --repo zebadee2kk/$REPO

# 2. Create backup branch
echo "Creating backup..."
SHA=$(gh api repos/zebadee2kk/$REPO/branches/$BRANCH --jq '.commit.sha')
gh api -X POST repos/zebadee2kk/$REPO/git/refs \
  -f ref="refs/heads/backup/$BRANCH" \
  -f sha="$SHA"

# 3. Verify backup
gh api repos/zebadee2kk/$REPO/branches/backup/$BRANCH

if [ $? -eq 0 ]; then
  echo "✅ Backup verified"
  
  # 4. Delete original
  echo "Deleting original branch..."
  gh api -X DELETE repos/zebadee2kk/$REPO/git/refs/heads/$BRANCH
  
  if [ $? -eq 0 ]; then
    echo "✅ Branch deleted successfully"
    echo "Backup available at: backup/$BRANCH"
  else
    echo "❌ Deletion failed"
  fi
else
  echo "❌ Backup verification failed - ABORTING"
fi
```

### Task 4.2: Cleanup Remaining Merged Branches

If test succeeds, process remaining branches:

```bash
# control-tower merged branches:
BRANCHES=(
  "fix-bug-6-concurrency"
  "phase-2.5-bug-fixes"
  "codex/perform-deep-review-of-control-tower-repository"
  "codex/conduct-overnight-review-of-workflows"
)

REPO="control-tower"

for branch in "${BRANCHES[@]}"; do
  echo ""
  echo "======================================"
  echo "Processing: $branch"
  echo "======================================"
  
  # Create backup
  SHA=$(gh api repos/zebadee2kk/$REPO/branches/$branch --jq '.commit.sha' 2>/dev/null)
  
  if [ -z "$SHA" ]; then
    echo "⚠️  Branch not found on remote (already deleted or never existed)"
    continue
  fi
  
  echo "Creating backup..."
  gh api -X POST repos/zebadee2kk/$REPO/git/refs \
    -f ref="refs/heads/backup/$branch" \
    -f sha="$SHA" 2>/dev/null
  
  # Delete original
  echo "Deleting original..."
  gh api -X DELETE repos/zebadee2kk/$REPO/git/refs/heads/$branch
  
  if [ $? -eq 0 ]; then
    echo "✅ Deleted: $branch (backup: backup/$branch)"
  else
    echo "❌ Failed to delete: $branch"
  fi
  
  echo "Press Enter to continue..."
  read
done

echo ""
echo "✅ Phase 1 cleanup complete!"
echo "Deleted 5 merged branches from control-tower"
echo "All backups available as backup/* branches"
```

---

## Phase 5: Enable Auto-Delete for Future

### Task 5.1: Configure Repository Settings

Help user enable auto-delete via web UI (can't do via API):

```
1. Visit: https://github.com/zebadee2kk/control-tower/settings
2. Scroll to "Pull Requests" section
3. Check: ☑️ "Automatically delete head branches"
4. Repeat for other active repos
```

---

## Phase 6: Verification & Cleanup

### Task 6.1: Verify Deletions

```bash
# Check remaining branches in control-tower:
gh api repos/zebadee2kk/control-tower/branches --jq '.[].name' | sort

# Should show:
# - main (default)
# - copilot/fix-bug-in-project-plan (open PR #48 - KEEP)
# - backup/* (all the backups)
```

### Task 6.2: Update Local Repos

```bash
cd ~/projects/control-tower
git fetch --prune
git branch -a

# User should see backup branches but not original merged branches
```

---

## Success Criteria

You've succeeded when:
- ✅ Audit run on all local repos
- ✅ No uncommitted changes or all handled
- ✅ No unpushed commits or all pushed
- ✅ 5 merged branches deleted from control-tower
- ✅ 5 backup branches created
- ✅ User's local repos sync without errors
- ✅ No data lost
- ✅ Auto-delete enabled on key repos

---

## Troubleshooting

### If User Gets "gh: command not found"

```bash
# Install GitHub CLI in WSL:
sudo apt update
sudo apt install gh

# Authenticate:
gh auth login
```

### If Branch Deletion Fails with 403

```bash
# Check authentication:
gh auth status

# Re-authenticate if needed:
gh auth refresh
```

### If Local Sync Shows Conflicts

```bash
# This shouldn't happen, but if it does:
cd ~/projects/REPO
git fetch --all
git status

# If on deleted branch:
git checkout main
git pull
```

---

## Next Phase (Future)

After immediate cleanup succeeds:
1. Review stale branches in ai-cost-tracker
2. Fix dual default branch issues (main/master)
3. Set up weekly automation
4. Integrate with control-tower project

See `branch_management_guide.md` for long-term strategy.

---

## Communication Tips for Copilot

- User is technically proficient but cautious (good!)
- Prefers understanding before executing
- Ask permission before destructive operations
- Explain what each command does
- Pause after each major phase for confirmation
- If anything looks wrong, STOP and ask user

---

## Files You Have Access To

- `branch_cleanup_report.json` - Full analysis data
- `branch_cleanup_summary.csv` - Quick reference
- `SAFETY_PROTOCOL.md` - Detailed safety procedures
- `cleanup_branches.sh` - Automated cleanup (use after audit)
- `branch_management_guide.md` - Long-term strategy

---

**Good luck! The user is counting on you to help execute this safely.**

---

Generated with ❤️ by Perplexity AI
Execution powered by GitHub Copilot

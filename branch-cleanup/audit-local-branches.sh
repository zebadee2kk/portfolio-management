#!/bin/bash
# audit-local-branches.sh
# Run this in each repository directory to check for uncommitted/unpushed work
# Generated: 2026-02-28 by Perplexity AI

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
  # Check if branch exists on remote
  if git ls-remote --heads origin "$CURRENT_BRANCH" 2>/dev/null | grep -q "$CURRENT_BRANCH"; then
    echo "  ℹ️  Branch exists on remote but not tracked" | tee -a "$OUTPUT_FILE"
    echo "  Fix: git branch --set-upstream-to=origin/$CURRENT_BRANCH" | tee -a "$OUTPUT_FILE"
  else
    echo "  ⚠️  LOCAL-ONLY BRANCH (never pushed!)" | tee -a "$OUTPUT_FILE"
    COMMITS=$(git log --oneline "$CURRENT_BRANCH" --not --remotes 2>/dev/null | wc -l)
    echo "  Commits: $COMMITS" | tee -a "$OUTPUT_FILE"
  fi
else
  UNPUSHED=$(git log --oneline "$TRACKING..$CURRENT_BRANCH" 2>/dev/null | wc -l)
  if [ "$UNPUSHED" -gt 0 ]; then
    echo "  ❌ WARNING: $UNPUSHED commits not pushed to $TRACKING!" | tee -a "$OUTPUT_FILE"
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

# 5. List all branches and their tracking status
echo "🌿 ALL BRANCHES WITH TRACKING INFO:" | tee -a "$OUTPUT_FILE"
for branch in $(git branch --format='%(refname:short)'); do
  tracking=$(git rev-parse --abbrev-ref "$branch@{upstream}" 2>/dev/null)
  if [ -z "$tracking" ]; then
    echo "  $branch -> (no upstream)" | tee -a "$OUTPUT_FILE"
  else
    ahead=$(git rev-list --count "$tracking..$branch" 2>/dev/null)
    behind=$(git rev-list --count "$branch..$tracking" 2>/dev/null)
    echo "  $branch -> $tracking [ahead $ahead, behind $behind]" | tee -a "$OUTPUT_FILE"
  fi
done
echo "" | tee -a "$OUTPUT_FILE"

# 6. Summary
echo "==================================================================" | tee -a "$OUTPUT_FILE"
echo "SUMMARY:" | tee -a "$OUTPUT_FILE"
echo "  Total local branches: $(git branch | wc -l)" | tee -a "$OUTPUT_FILE"
echo "  Uncommitted files: $(git status --short | wc -l)" | tee -a "$OUTPUT_FILE"
echo "  Stashes: $(git stash list | wc -l)" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Check for warnings
if grep -q "WARNING\|❌" "$OUTPUT_FILE"; then
  echo "⚠️  ATTENTION REQUIRED: Uncommitted or unpushed work found!" | tee -a "$OUTPUT_FILE"
  echo "Review the warnings above before proceeding with cleanup." | tee -a "$OUTPUT_FILE"
else
  echo "✅ Repository is clean and safe for remote branch cleanup" | tee -a "$OUTPUT_FILE"
fi

echo "" | tee -a "$OUTPUT_FILE"
echo "Audit complete. Full output saved to:" | tee -a "$OUTPUT_FILE"
echo "  $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"
echo "==================================================================" | tee -a "$OUTPUT_FILE"

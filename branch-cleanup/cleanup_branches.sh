#!/bin/bash
# Branch Cleanup Script for zebadee2kk repositories
# Generated: 2026-02-28
# Execute this script carefully - review each section before running

set -e  # Exit on error

echo "========================================================================"
echo "GITHUB BRANCH CLEANUP SCRIPT"
echo "========================================================================"
echo ""
echo "⚠️  IMPORTANT: Review each command before executing"
echo "This script is divided into sections for safety"
echo ""

# =============================================================================
# PHASE 1: IMMEDIATE CLEANUP - Merged PR Branches
# =============================================================================

echo ""
echo "========================================================================"
echo "PHASE 1: Delete Merged PR Branches (5 branches)"
echo "========================================================================"
echo ""

echo "Repository: control-tower"
echo "These branches were merged and can be safely deleted:"
echo ""

# control-tower - 5 merged branches
gh api -X DELETE repos/zebadee2kk/control-tower/git/refs/heads/docs-phase-2-5-handoff && echo "  ✅ Deleted: docs-phase-2-5-handoff (PR #41 merged 2026-02-25)"
gh api -X DELETE repos/zebadee2kk/control-tower/git/refs/heads/fix-bug-6-concurrency && echo "  ✅ Deleted: fix-bug-6-concurrency (PR #40 merged 2026-02-25)"
gh api -X DELETE repos/zebadee2kk/control-tower/git/refs/heads/phase-2.5-bug-fixes && echo "  ✅ Deleted: phase-2.5-bug-fixes (PR #21 merged 2026-02-25)"
gh api -X DELETE "repos/zebadee2kk/control-tower/git/refs/heads/codex/perform-deep-review-of-control-tower-repository" && echo "  ✅ Deleted: codex/perform-deep-review-of-control-tower-repository (PR #17 merged 2026-02-24)"
gh api -X DELETE "repos/zebadee2kk/control-tower/git/refs/heads/codex/conduct-overnight-review-of-workflows" && echo "  ✅ Deleted: codex/conduct-overnight-review-of-workflows (PR #16 merged 2026-02-24)"

echo ""
echo "✅ Phase 1 Complete: 5 merged branches deleted"
echo ""

# =============================================================================
# PHASE 2: DEFAULT BRANCH STANDARDIZATION
# =============================================================================

echo ""
echo "========================================================================"
echo "PHASE 2: Standardize Default Branches"
echo "========================================================================"
echo ""
echo "⚠️  ACTION REQUIRED: Two repositories have both 'main' and 'master' branches"
echo ""

echo "Repository: ai-cost-tracker"
echo "  Current default: master"
echo "  Recommendation: Switch to 'main' for consistency"
echo ""
echo "  Manual steps required:"
echo "  1. Review if 'main' and 'master' branches are identical:"
echo "     git clone git@github.com:zebadee2kk/ai-cost-tracker.git"
echo "     cd ai-cost-tracker"
echo "     git diff master..main"
echo ""
echo "  2. If identical, delete 'main' branch:"
echo "     gh api -X DELETE repos/zebadee2kk/ai-cost-tracker/git/refs/heads/main"
echo ""
echo "  3. If different, merge unique commits from 'main' to 'master' first"
echo "  4. OPTIONAL: Rename 'master' to 'main' for modern naming:"
echo "     gh api -X PATCH repos/zebadee2kk/ai-cost-tracker -f default_branch=main"
echo ""

echo "Repository: ai-powertools"
echo "  Current default: master"
echo "  Same procedure as ai-cost-tracker above"
echo ""

# =============================================================================
# PHASE 3: STALE BRANCH REVIEW
# =============================================================================

echo ""
echo "========================================================================"
echo "PHASE 3: Review Stale Branches (Manual Review Required)"
echo "========================================================================"
echo ""
echo "The following branches have no associated open PRs."
echo "Check with 'git log' if they contain valuable unpushed work:"
echo ""

echo "Repository: kynee"
echo "  Branch: codex/review-project-and-provide-recommendations"
echo "  Action: Check for commits not in main:"
echo "    git log main..codex/review-project-and-provide-recommendations"
echo "  Delete if empty:"
echo "    gh api -X DELETE repos/zebadee2kk/kynee/git/refs/heads/codex/review-project-and-provide-recommendations"
echo ""

echo "Repository: portfolio-management"
echo "  Branch: copilot/start-project-as-per-plan"
echo "  Action: Check for commits not in main:"
echo "    git log main..copilot/start-project-as-per-plan"
echo "  Delete if empty:"
echo "    gh api -X DELETE repos/zebadee2kk/portfolio-management/git/refs/heads/copilot/start-project-as-per-plan"
echo ""

echo "Repository: ai-cost-tracker (14 feature branches)"
echo "  All claude/* and codex/* branches require review"
echo "  Use this command to check each:"
echo "    gh pr list --repo zebadee2kk/ai-cost-tracker --head BRANCH_NAME"
echo "  If no PRs exist and branch is old, consider deletion"
echo ""

# =============================================================================
# PHASE 4: PROTECT ACTIVE WORK
# =============================================================================

echo ""
echo "========================================================================"
echo "PHASE 4: Branches to KEEP (Active Work)"
echo "========================================================================"
echo ""
echo "DO NOT DELETE these branches - they have open PRs:"
echo ""
echo "Repository: control-tower"
echo "  ✋ KEEP: copilot/fix-bug-in-project-plan (Open draft PR #48)"
echo ""

# =============================================================================
# COMPLETION AND BEST PRACTICES
# =============================================================================

echo ""
echo "========================================================================"
echo "CLEANUP COMPLETE - NEXT STEPS"
echo "========================================================================"
echo ""
echo "✅ Recommended: Enable auto-delete for merged PR branches"
echo "   Settings → Pull Requests → 'Automatically delete head branches'"
echo ""
echo "✅ Setup branch protection for 'main' branches"
echo "   Settings → Branches → Add branch protection rule"
echo ""
echo "✅ Consider adding this to your weekly routine:"
echo "   gh api repos/zebadee2kk/REPO_NAME/branches --jq '.[] | select(.name != \"main\" and .name != \"master\") | .name'"
echo ""
echo "📊 Summary:"
echo "  • Deleted: 5 merged branches"
echo "  • To review: 16+ branches across repositories"
echo "  • Default branch conflicts: 2 repos need standardization"
echo ""

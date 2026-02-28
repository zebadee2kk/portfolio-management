# Branch Management Best Practices for AI-Native Development
## Prevention Guide for zebadee2kk Portfolio

Generated: 2026-02-28

---

## Current Situation

You have **30+ branches across 5 analyzed repositories**, with:
- 5 branches safe to delete immediately (merged PRs)
- 2 repositories with dual default branches (main/master conflict)
- 16+ feature branches requiring manual review
- Pattern: AI assistants (Claude, Codex, Copilot) creating numerous feature branches

---

## Root Causes

### 1. AI Assistant Workflow Pattern
- **Claude, Codex, and Copilot** automatically create feature branches
- Each AI task spawns a new branch
- No automatic cleanup after PR merge
- Rapid iteration creates branch proliferation

### 2. Manual Workflow Gaps
- No branch protection rules enabled
- Auto-delete on merge not configured
- No periodic cleanup routine
- Inconsistent default branch naming (main vs master)

---

## Recommended Solutions

### Phase 1: Immediate Configuration (30 minutes)

#### Enable Auto-Delete on Merge
For each repository, navigate to:
```
Settings → General → Pull Requests
☑️ Automatically delete head branches
```

**Impact**: Eliminates 80% of future branch accumulation

#### Standardize Default Branches
**Decision**: Use `main` as standard across all repos

**Action for ai-cost-tracker and ai-powertools**:
1. Check for divergence: `git diff master..main`
2. If identical: Delete `main` branch
3. If master has no unique work: Switch default to `main`, delete `master`
4. Update local clones: `git branch -m master main && git push -u origin main`

### Phase 2: Automation Setup (1 hour)

#### Option A: GitHub Actions Weekly Cleanup
Create `.github/workflows/branch-cleanup.yml`:

```yaml
name: Stale Branch Cleanup
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Delete merged branches
        uses: phpdave11/gha-remove-merged-branches@v1.0.0
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          exclude_branches: 'main,master,develop,staging,production'
```

#### Option B: Local Script (Cron Job)
Add to your homelab automation (Proxmox LXC):

```bash
#!/bin/bash
# Add to: ~/scripts/github-branch-cleanup.sh
# Cron: 0 3 * * 0 (Weekly Sunday 3 AM)

REPOS=(
  "control-tower"
  "ai-cost-tracker"
  "kynee"
  "portfolio-management"
  "ai-powertools"
  # Add all 16 repos
)

for repo in "${REPOS[@]}"; do
  echo "Cleaning $repo..."
  gh api "repos/zebadee2kk/$repo/branches" --jq '.[] | select(.name != "main" and .name != "master") | .name' | while read branch; do
    # Check if branch has open PR
    pr_count=$(gh pr list --repo "zebadee2kk/$repo" --head "$branch" --json number --jq 'length')
    if [ "$pr_count" -eq 0 ]; then
      # Check last commit date
      last_commit=$(gh api "repos/zebadee2kk/$repo/branches/$branch" --jq '.commit.commit.committer.date')
      echo "  Branch: $branch (last commit: $last_commit)"
      # Add logic to delete if > 30 days old
    fi
  done
done
```

### Phase 3: Branch Protection Rules (15 minutes per repo)

For primary repositories (control-tower, portfolio-management):

```
Settings → Branches → Add branch protection rule
```

Configure:
- Branch name pattern: `main`
- ☑️ Require pull request before merging
- ☑️ Require status checks to pass
- ☑️ Require branches to be up to date
- ☑️ Include administrators (optional for solo dev)

### Phase 4: AI Assistant Integration

#### Update AI Assistant Prompts
Add to your Claude/Codex/Copilot context files:

```markdown
## Branch Naming Convention
- Format: `<assistant>/<feature>-<random-suffix>`
- Examples: `claude/fix-auth-bug-x7k2q`, `codex/review-api-docs`

## Post-Merge Protocol
After PR approval:
1. Verify merge to main
2. Delete feature branch: `gh api -X DELETE repos/zebadee2kk/REPO/git/refs/heads/BRANCH`
3. Update local workspace: `git branch -d BRANCH`
```

#### Control-Tower Integration
Since you're building control-tower as a GitHub-native control plane:

Add cleanup job to `docs/PROJECT_PLAN.md`:
```markdown
### Phase 3: Housekeeping Automation
- Weekly stale branch detection
- Auto-delete merged branches >7 days old
- Report branches without PRs
- Notify on default branch conflicts
```

---

## Implementation Timeline

### Week 1 (Now): Emergency Cleanup
- ✅ Run `cleanup_branches.sh` - delete 5 merged branches
- ✅ Enable auto-delete on merge for top 5 repos
- ✅ Resolve dual default branch conflicts (ai-cost-tracker, ai-powertools)

### Week 2: Automation
- Create weekly cleanup GitHub Action OR cron job
- Test on 2-3 repos before rolling out to all 16
- Document in portfolio-management repo

### Week 3: Protection
- Add branch protection to main branches (control-tower, kynee, portfolio-management)
- Update local git configs to default to `main` instead of `master`

### Ongoing: Monitoring
- Review branch count monthly
- Adjust cleanup thresholds based on actual workflow
- Update AI assistant prompts as needed

---

## Success Metrics

After 30 days, you should see:
- ✅ No repositories with >5 branches
- ✅ All merged PR branches auto-deleted within 24 hours
- ✅ Consistent `main` as default across all repos
- ✅ Stale branches flagged weekly
- ✅ Zero manual branch management required

---

## Integration with Existing Projects

### Control-Tower
Your GitHub-native control plane should handle this automatically:
- Add branch cleanup to workflow automation
- Create "housekeeping" workflow triggered weekly
- Report stale branches to Decision Desk

### Portfolio-Management
Track branch health metrics:
- Branches per repo
- Average branch lifetime
- Stale branch detection
- Alert when any repo exceeds 10 branches

---

## Quick Reference Commands

```bash
# List all branches in a repo
gh api repos/zebadee2kk/REPO/branches --jq '.[].name'

# Delete a specific branch
gh api -X DELETE repos/zebadee2kk/REPO/git/refs/heads/BRANCH

# Check for open PRs on a branch
gh pr list --repo zebadee2kk/REPO --head BRANCH

# Find merged branches (no longer needed)
gh pr list --repo zebadee2kk/REPO --state merged --json headRefName --jq '.[].headRefName'

# Enable auto-delete (requires web UI)
# Settings → General → Pull Requests → Auto-delete head branches
```

---

## Notes for AI-Native Workflow

Your heavy use of Claude, Codex, and Copilot is actually a strength, but requires:

1. **Structured handoff protocols** between AI sessions
2. **Explicit cleanup steps** in AI task completion
3. **Automated hygiene** to compensate for AI branch creation rate
4. **Central coordination** (control-tower) to manage AI-generated branches

This is a governance problem, not a technical one. The solution is automation + policy, not manual intervention.

---

## Support Resources

- GitHub Branch Management: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository
- GitHub CLI Reference: https://cli.github.com/manual/gh_api
- Branch Protection Rules: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

---

Generated by Perplexity AI for zebadee2kk
2026-02-28

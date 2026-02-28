# 🛡️ SAFETY PROTOCOL: Protecting Uncommitted Local Changes
## Before Deleting Remote Branches

Generated: 2026-02-28 13:27 GMT

---

## ⚠️ CRITICAL RISK YOU IDENTIFIED

You're correct! If you have:
- Local branches with uncommitted changes
- Local commits not yet pushed to GitHub
- Work-in-progress code on any of your machines (laptop, Proxmox VMs, etc.)

**Deleting remote branches will NOT affect local code**, BUT you could lose track of what 
needs to be pushed/merged. Here's how to protect yourself:

---

## STEP 1: Audit Local Branches on Windows Laptop

Run the audit script to discover:
- All local branches you have
- Uncommitted changes (files not committed)
- Unpushed commits (commits not on GitHub)
- Local-only branches (branches never pushed)
- Stashed changes

### Run This First

```bash
# In WSL Ubuntu on your Windows laptop:
cd ~/projects  # or wherever you keep repos

# For each repo you have locally:
for repo in control-tower ai-cost-tracker kynee portfolio-management ai-powertools; do
  if [ -d "$repo" ]; then
    echo "Auditing $repo..."
    cd "$repo"
    bash ../branch-cleanup/audit-local-branches.sh
    cd ..
  fi
done
```

### What the Audit Reveals

The script will create output files showing:
- ✅ Clean branches (safe to delete remote)
- ⚠️ Branches with uncommitted changes (DON'T delete remote yet)
- ⚠️ Branches with unpushed commits (push first, then delete)
- ℹ️ Local-only branches (never existed on remote)

---

## STEP 2: Review Audit Output

Look for these warning signs:

```
❌ WARNING: You have uncommitted changes!
❌ WARNING: X commits not pushed to origin/branch-name
⚠️ LOCAL-ONLY BRANCH (never pushed to remote!)
⚠️ WARNING: You have stashed changes that need review!
```

If you see ANY of these:
1. **Stop** - Don't delete any remote branches yet
2. **Decide** - Do you need this work?
3. **Act** - Commit, push, or discard

---

## STEP 3: Safe Actions Before Cleanup

### For Uncommitted Changes

```bash
# Option A: Commit them
git add .
git commit -m "WIP: Saving uncommitted changes before cleanup"
git push

# Option B: Stash them
git stash save "Before branch cleanup - 2026-02-28"

# Option C: Discard them (if truly not needed)
git restore .  # Careful! This is destructive
```

### For Unpushed Commits

```bash
# Push them before deleting remote branch
git push origin branch-name

# Or create a backup branch
git branch backup/branch-name branch-name
git push origin backup/branch-name
```

### For Local-Only Branches

```bash
# These are safe - they only exist on your machine
# Deleting remote branches won't affect them
# But you might want to push them:
git push -u origin branch-name
```

---

## STEP 4: Backup Strategies

### Strategy 1: Backup Branches (Recommended)

Before deleting remote branch, create backup:

```bash
# For each branch you'll delete:
gh api -X POST repos/zebadee2kk/REPO/git/refs \
  -f ref="refs/heads/backup/BRANCH-NAME" \
  -f sha=$(gh api repos/zebadee2kk/REPO/branches/BRANCH-NAME --jq '.commit.sha')

# Then safe to delete original:
gh api -X DELETE repos/zebadee2kk/REPO/git/refs/heads/BRANCH-NAME
```

### Strategy 2: Export as Patches

```bash
# Create patch files:
mkdir -p ~/branch-backups
for branch in branch1 branch2 branch3; do
  git format-patch main..$branch --stdout > ~/branch-backups/$branch.patch
done

# Restore later:
git apply ~/branch-backups/BRANCH-NAME.patch
```

### Strategy 3: Full Repository Mirror

```bash
# Complete backup before any changes:
git clone --mirror git@github.com:zebadee2kk/REPO.git ~/backups/REPO-$(date +%Y%m%d).git
```

---

## STEP 5: The Safe Cleanup Process

### Phase 0: Pre-Flight ✅

- [ ] Audit script run on Windows laptop
- [ ] Audit output reviewed
- [ ] All uncommitted changes handled
- [ ] All unpushed commits pushed
- [ ] Backup strategy chosen

### Phase 1: Test with One Branch

```bash
# Pick ONE merged branch to test:
BRANCH="docs-phase-2-5-handoff"
REPO="control-tower"

# 1. Verify it's merged
gh pr list --repo zebadee2kk/$REPO --head $BRANCH --state merged

# 2. Create backup
gh api -X POST repos/zebadee2kk/$REPO/git/refs \
  -f ref="refs/heads/backup/$BRANCH" \
  -f sha=$(gh api repos/zebadee2kk/$REPO/branches/$BRANCH --jq '.commit.sha')

# 3. Delete original
gh api -X DELETE repos/zebadee2kk/$REPO/git/refs/heads/$BRANCH

# 4. Verify backup exists
gh api repos/zebadee2kk/$REPO/branches/backup/$BRANCH

# 5. Test local sync
cd ~/projects/$REPO
git fetch --prune
git branch -a  # Should show backup/BRANCH but not BRANCH
```

### Phase 2: Proceed with Remaining Branches

Once test succeeds, use the automated scripts in this directory.

---

## STEP 6: Recovery Procedures

### If You Accidentally Delete Something Important

```bash
# 1. Check for backup branch
gh api repos/zebadee2kk/REPO/branches/backup/BRANCH-NAME

# 2. Restore from backup
git fetch origin
git checkout -b BRANCH-NAME origin/backup/BRANCH-NAME

# 3. Push restored branch
git push -u origin BRANCH-NAME
```

### If No Backup Exists

```bash
# GitHub keeps commits for ~30 days
# Find commit SHA from PR page, then:
git fetch origin
git checkout -b recovered-branch COMMIT-SHA
git push -u origin recovered-branch
```

---

## Key Principles

1. **Local branches are never affected by remote deletion**
   - Your files are safe on your laptop
   - Your commits are safe on your laptop
   - Only the remote pointer is deleted

2. **The risk is losing track, not losing data**
   - You might forget to push important work
   - You might not realize you have unpushed commits
   - Audit prevents this

3. **Backups provide insurance**
   - backup/* branches are cheap
   - Patch files are portable
   - Mirrors are comprehensive

4. **Test first, automate second**
   - Manual test on one branch builds confidence
   - Automation speeds up remaining work
   - But audit comes before both

---

## Questions Checklist

Before proceeding, answer:

- [ ] Have I run the audit script?
- [ ] Have I reviewed all audit outputs?
- [ ] Do I have uncommitted changes that need handling?
- [ ] Do I have unpushed commits that need pushing?
- [ ] Have I chosen a backup strategy?
- [ ] Have I tested on one branch first?
- [ ] Am I confident I won't lose work?

---

## Next Steps

Once all checks pass, proceed to:
1. `HANDOVER_TO_COPILOT.md` - Let VS Code Copilot help execute
2. `cleanup_branches.sh` - Automated cleanup with safety checks
3. `branch_management_guide.md` - Long-term prevention

---

**Remember**: This is about risk management, not technical capability. 
The audit is your safety net.

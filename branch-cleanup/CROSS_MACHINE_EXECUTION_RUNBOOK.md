# Branch Cleanup Execution + Cross-Machine Runbook

Generated: 2026-02-28
Owner: zebadee2kk

---

## 1) What Was Executed (This Machine)

### Completed cleanup actions

- **control-tower**: 5 merged branches backed up and deleted
  - `docs-phase-2-5-handoff`
  - `fix-bug-6-concurrency`
  - `phase-2.5-bug-fixes`
  - `codex/perform-deep-review-of-control-tower-repository`
  - `codex/conduct-overnight-review-of-workflows`

- **ai-cost-tracker**: 14 merged branches backed up and deleted
  - `claude/phase-3-implementation-hLBRj`
  - `claude/fix-security-issues-lVxbV`
  - `main`
  - `codex/establish-pr-review-process-for-codex`
  - `claude/export-endpoint-streaming-4OBH1`
  - `codex/conduct-project-handover-for-next-steps`
  - `claude/review-changes-mm2o0cx98svo47hd-K9F90`
  - `codex/run-code-check-and-review`
  - `claude/multi-service-cost-tracker-WQTIj`
  - `codex/review-ci/cd-pipeline-setup-pr`
  - `codex/review-session-and-check-handover-process`
  - `claude/notification-db-migrations-JDEyn`
  - `codex/review-pr-#17-and-document-results`
  - `codex/verify-pr-#20-for-issue-remediation`

- **kynee**: 1 merged branch backed up and deleted
  - `codex/review-project-and-provide-recommendations`

### Execution evidence

- Detailed machine log: `branch-cleanup/cleanup-execution-20260228.tsv`
- Local WIP was protected by stashes in local clones before cleanup.

---

## 2) Current Post-Cleanup State

### Clean repos (no remaining non-default non-backup branches)

- `ai-cost-tracker`
- `kynee`
- `xai-sdk-python-fork`
- `zebadee2kk`
- `zebra-ecosystem`

### Remaining branches intentionally kept

- `control-tower`: `copilot/fix-bug-in-project-plan` (open PR)
- `portfolio-management`: `copilot/start-project-as-per-plan` (open PR)
- `best-practice-repo-template`: several `dependabot/*` branches (open PRs)
- `ai-powertools`:
  - `copilot/understand-repo-purpose` (open PR)
  - `main` (kept due divergence from `master`)

### ai-powertools branch conflict

`master...main` compare result was **diverged** (`ahead_by=1`, `behind_by=1`), so `main` was **not** auto-deleted.

**Resolution**: See [AI_POWERTOOLS_RECONCILIATION.md](AI_POWERTOOLS_RECONCILIATION.md) for detailed merge instructions with exact commands.

---

## 3) Run This on Other Dev Machines

> Goal: protect local work first, then sync with remote cleanup.

### Step A: Local safety audit (required)

```bash
cd ~/projects

# For each locally cloned repo
for repo in control-tower ai-cost-tracker kynee portfolio-management ai-powertools best-practice-repo-template xai-sdk-python-fork zebadee2kk zebra-ecosystem; do
  if [ -d "$repo" ]; then
    cd "$repo"
    bash ../portfolio-management/branch-cleanup/audit-local-branches.sh
    cd ..
  fi
done

# Review warnings quickly
grep -hE "WARNING|❌" ~/branch-audit-*.txt
```

If warnings exist, do one of:

```bash
# Commit
git add . && git commit -m "WIP before branch cleanup" && git push

# or stash
git stash push -u -m "Before branch cleanup $(date +%F-%T)"
```

### Step B: Sync local refs to reflect remote cleanup

```bash
cd ~/projects
for repo in control-tower ai-cost-tracker kynee portfolio-management ai-powertools best-practice-repo-template xai-sdk-python-fork zebadee2kk zebra-ecosystem; do
  if [ -d "$repo/.git" ]; then
    cd "$repo"
    git fetch --prune --all
    cd ..
  fi
done
```

### Step C: Restore local WIP if needed

```bash
git stash list
git stash pop   # only when ready
```

---

## 4) Optional: Re-run Safe Remote Cleanup Later

Use this policy:

1. Only delete branches that are from **merged PRs**.
2. Always create `backup/<branch>` first.
3. Never delete default branch.
4. Skip open PR branches.

Core command pattern:

```bash
# get SHA
SHA=$(gh api repos/zebadee2kk/REPO/branches/BRANCH --jq '.commit.sha')

# backup
gh api -X POST repos/zebadee2kk/REPO/git/refs \
  -f ref="refs/heads/backup/BRANCH" \
  -f sha="$SHA"

# delete original
gh api -X DELETE repos/zebadee2kk/REPO/git/refs/heads/BRANCH
```

---

## 5) Manual Follow-ups

1. Enable auto-delete in each key repo:
   - **Settings → Pull Requests → Automatically delete head branches**
2. Resolve `ai-powertools` `main` vs `master` divergence:
   - Merge/cherry-pick unique commits, then choose one default branch.
3. Optionally add a weekly branch hygiene check in GitHub Actions.

---

## 6) Mac Dev Machine Finalization (2026-02-28)

Mac local synchronization and no-data-loss finalization is documented in:

- `MAC_DEV_MACHINE_SYNC_20260228.md`

This includes:
- local repo discovery on Mac
- safety audit + fetch/prune + fast-forward pull execution
- temporary backup/stash protections
- final active branch setup (`zebra-ecosystem` on `wip/restore-stash-20260228`)
- post-verification cleanup of temporary safety artifacts

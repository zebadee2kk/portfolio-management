"""Project prioritization logic."""

from __future__ import annotations

import math

from portfolio_manager.models import (
    PrioritizedRepo,
    PriorityLevel,
    PriorityScore,
    Repository,
)


class ProjectPrioritizer:
    """Score and rank repositories by their development priority.

    Scoring is intentionally simple and deterministic so results are
    reproducible without an LLM.  Scores are returned on a 0–100 scale.

    Factors
    -------
    activity_score (40 pts)
        Based on days since last push.  A repo pushed today scores 40;
        one untouched for ≥365 days scores 0.

    engagement_score (30 pts)
        Logarithmic star + fork count.  High star counts indicate community
        value and therefore raise priority.

    health_score (20 pts)
        Ratio of open issues to activity.  A large backlog on an active repo
        scores high; a large backlog on a stale repo scores low.

    recency_score (10 pts)
        Age of the repository.  Newer repos score slightly higher to reflect
        the energy already invested in starting them.
    """

    # Maximum contribution from each factor
    _WEIGHTS = {
        "activity": 40.0,
        "engagement": 30.0,
        "health": 20.0,
        "recency": 10.0,
    }

    def prioritize(self, repos: list[Repository]) -> list[PrioritizedRepo]:
        """Return *repos* sorted from highest to lowest priority."""
        results = [self._score_repo(repo) for repo in repos]
        results.sort(key=lambda pr: pr.score.total, reverse=True)
        return results

    def _score_repo(self, repo: Repository) -> PrioritizedRepo:
        activity = self._activity_score(repo)
        engagement = self._engagement_score(repo)
        health = self._health_score(repo)
        recency = self._recency_score(repo)

        # Archived repos are always lowest priority
        if repo.is_archived:
            level = PriorityLevel.ARCHIVED
            total = 0.0
        else:
            total = activity + engagement + health + recency
            level = self._level(total)

        score = PriorityScore(
            total=round(total, 2),
            activity_score=round(activity, 2),
            engagement_score=round(engagement, 2),
            health_score=round(health, 2),
            recency_score=round(recency, 2),
            level=level,
        )
        return PrioritizedRepo(
            repo=repo,
            score=score,
            suggested_actions=self._suggest_actions(repo, score),
        )

    # ------------------------------------------------------------------
    # Individual factor calculations
    # ------------------------------------------------------------------

    def _activity_score(self, repo: Repository) -> float:
        days = repo.days_since_push
        if days is None:
            return 0.0
        # Linear decay: full score at 0 days, zero at 365+ days
        fraction = max(0.0, 1.0 - days / 365.0)
        return self._WEIGHTS["activity"] * fraction

    def _engagement_score(self, repo: Repository) -> float:
        combined = repo.stars + repo.forks
        if combined == 0:
            return 0.0
        # Logarithmic scale: log10(1000 stars) ≈ 3, cap at the weight
        fraction = min(1.0, math.log10(combined + 1) / 3.0)
        return self._WEIGHTS["engagement"] * fraction

    def _health_score(self, repo: Repository) -> float:
        if repo.open_issues == 0:
            # No open issues: moderately healthy
            return self._WEIGHTS["health"] * 0.5
        days = repo.days_since_push or 365
        # Active repos with issues score high; stale ones with issues score low
        activity_factor = max(0.0, 1.0 - days / 180.0)
        issue_factor = min(1.0, math.log10(repo.open_issues + 1) / 2.0)
        return self._WEIGHTS["health"] * activity_factor * issue_factor

    def _recency_score(self, repo: Repository) -> float:
        if repo.created_at is None:
            return 0.0
        from datetime import datetime, timezone

        age_days = (datetime.now(tz=timezone.utc) - repo.created_at.replace(tzinfo=timezone.utc)).days
        # Full score for repos created in the last year, decays over 3 years
        fraction = max(0.0, 1.0 - age_days / (3 * 365))
        return self._WEIGHTS["recency"] * fraction

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _level(total: float) -> PriorityLevel:
        if total >= 70:
            return PriorityLevel.CRITICAL
        if total >= 50:
            return PriorityLevel.HIGH
        if total >= 25:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW

    @staticmethod
    def _suggest_actions(repo: Repository, score: PriorityScore) -> list[str]:
        actions: list[str] = []
        if repo.is_archived:
            actions.append("Consider unarchiving if still relevant.")
            return actions
        days = repo.days_since_push
        if days is not None and days > 180:
            actions.append(f"Repo is stale ({days} days since last push) — review or archive.")
        if repo.open_issues > 10:
            actions.append(f"High open-issue count ({repo.open_issues}) — triage backlog.")
        if not repo.description:
            actions.append("Add a repository description for discoverability.")
        if not repo.topics:
            actions.append("Add topics/tags to improve searchability.")
        if score.level in (PriorityLevel.CRITICAL, PriorityLevel.HIGH) and not repo.is_active:
            actions.append("High-priority repo is inactive — schedule a sprint.")
        return actions

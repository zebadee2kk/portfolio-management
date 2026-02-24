"""Cross-repository coordination and portfolio reporting."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from portfolio_manager.models import (
    PortfolioReport,
    PrioritizedRepo,
    PriorityLevel,
    Repository,
)


class RepoCoordinator:
    """Aggregate prioritised repository data into actionable portfolio reports."""

    def generate_report(
        self,
        owner: str,
        prioritized: list[PrioritizedRepo],
    ) -> PortfolioReport:
        """Build a :class:`PortfolioReport` from a prioritised repo list."""
        repos = [pr.repo for pr in prioritized]

        lang_counter: Counter[str] = Counter()
        topic_counter: Counter[str] = Counter()
        active = stale = archived = 0

        for repo in repos:
            if repo.is_archived:
                archived += 1
            elif repo.is_active:
                active += 1
            else:
                stale += 1

            if repo.language:
                lang_counter[repo.language] += 1

            for topic in repo.topics:
                topic_counter[topic] += 1

        top_topics = [t for t, _ in topic_counter.most_common(10)]

        return PortfolioReport(
            owner=owner,
            generated_at=datetime.now(tz=timezone.utc),
            total_repos=len(repos),
            active_repos=active,
            stale_repos=stale,
            archived_repos=archived,
            prioritized=prioritized,
            languages=dict(lang_counter.most_common()),
            top_topics=top_topics,
            focus_suggestions=self._focus_suggestions(prioritized),
        )

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------

    def group_by_language(self, repos: list[Repository]) -> dict[str, list[Repository]]:
        """Group repositories by their primary language."""
        groups: dict[str, list[Repository]] = {}
        for repo in repos:
            lang = repo.language or "Unknown"
            groups.setdefault(lang, []).append(repo)
        return groups

    def identify_active(self, repos: list[Repository]) -> list[Repository]:
        """Return only the repositories active in the last 90 days."""
        return [r for r in repos if r.is_active]

    def identify_stale(
        self, repos: list[Repository], threshold_days: int = 180
    ) -> list[Repository]:
        """Return repositories that have not been pushed to in *threshold_days*."""
        results = []
        for repo in repos:
            days = repo.days_since_push
            if days is not None and days >= threshold_days and not repo.is_archived:
                results.append(repo)
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _focus_suggestions(prioritized: list[PrioritizedRepo]) -> list[str]:
        suggestions: list[str] = []

        critical = [
            pr.repo.full_name
            for pr in prioritized
            if pr.score.level == PriorityLevel.CRITICAL
        ]
        high = [
            pr.repo.full_name
            for pr in prioritized
            if pr.score.level == PriorityLevel.HIGH
        ]
        stale_high = [
            pr.repo.full_name
            for pr in prioritized
            if pr.score.level in (PriorityLevel.HIGH, PriorityLevel.CRITICAL)
            and not pr.repo.is_active
        ]

        if critical:
            suggestions.append(
                f"🔴 Critical priority: {', '.join(critical[:5])}. Focus here first."
            )
        if high:
            suggestions.append(
                f"🟠 High priority: {', '.join(high[:5])}. Schedule work soon."
            )
        if stale_high:
            suggestions.append(
                f"⚠️  High-value repos gone stale: {', '.join(stale_high[:3])}. "
                "Consider a revival sprint."
            )

        no_desc = [
            pr.repo.full_name
            for pr in prioritized
            if not pr.repo.description and not pr.repo.is_archived
        ]
        if no_desc:
            suggestions.append(
                f"📝 {len(no_desc)} repos lack descriptions — add them for discoverability."
            )

        return suggestions

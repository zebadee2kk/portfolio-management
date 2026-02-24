"""Tests for portfolio_manager.coordinator."""

from datetime import datetime, timedelta, timezone

from portfolio_manager.coordinator import RepoCoordinator
from portfolio_manager.models import (
    PrioritizedRepo,
    PriorityLevel,
    PriorityScore,
    Repository,
)


def _make_repo(name: str, *, language: str = "Python", days_since_push: int = 10, is_archived: bool = False) -> Repository:
    now = datetime.now(tz=timezone.utc)
    return Repository(
        name=name,
        full_name=f"user/{name}",
        url=f"https://api.github.com/repos/user/{name}",
        html_url=f"https://github.com/user/{name}",
        language=language,
        pushed_at=now - timedelta(days=days_since_push),
        created_at=now - timedelta(days=365),
        is_archived=is_archived,
        description=f"Description for {name}",
    )


def _make_prioritized(repo: Repository, level: PriorityLevel = PriorityLevel.MEDIUM) -> PrioritizedRepo:
    score = PriorityScore(
        total=50.0,
        activity_score=20.0,
        engagement_score=15.0,
        health_score=10.0,
        recency_score=5.0,
        level=level,
    )
    return PrioritizedRepo(repo=repo, score=score)


class TestRepoCoordinator:
    def setup_method(self):
        self.coordinator = RepoCoordinator()

    def test_generate_report_counts(self):
        repos = [
            _make_prioritized(_make_repo("active1", days_since_push=5)),
            _make_prioritized(_make_repo("stale1", days_since_push=200)),
            _make_prioritized(_make_repo("archived1", is_archived=True), level=PriorityLevel.ARCHIVED),
        ]
        report = self.coordinator.generate_report("user", repos)
        assert report.total_repos == 3
        assert report.active_repos == 1
        assert report.stale_repos == 1
        assert report.archived_repos == 1

    def test_generate_report_languages(self):
        repos = [
            _make_prioritized(_make_repo("py1", language="Python")),
            _make_prioritized(_make_repo("py2", language="Python")),
            _make_prioritized(_make_repo("js1", language="JavaScript")),
        ]
        report = self.coordinator.generate_report("user", repos)
        assert report.languages["Python"] == 2
        assert report.languages["JavaScript"] == 1

    def test_group_by_language(self):
        repos = [
            _make_repo("py1", language="Python"),
            _make_repo("py2", language="Python"),
            _make_repo("go1", language="Go"),
        ]
        groups = self.coordinator.group_by_language(repos)
        assert len(groups["Python"]) == 2
        assert len(groups["Go"]) == 1

    def test_identify_active(self):
        repos = [
            _make_repo("active", days_since_push=10),
            _make_repo("stale", days_since_push=200),
        ]
        active = self.coordinator.identify_active(repos)
        assert len(active) == 1
        assert active[0].name == "active"

    def test_identify_stale(self):
        repos = [
            _make_repo("active", days_since_push=10),
            _make_repo("stale", days_since_push=200),
        ]
        stale = self.coordinator.identify_stale(repos)
        assert len(stale) == 1
        assert stale[0].name == "stale"

    def test_focus_suggestions_critical(self):
        repo = _make_repo("critical-repo")
        pr = _make_prioritized(repo, level=PriorityLevel.CRITICAL)
        report = self.coordinator.generate_report("user", [pr])
        assert any("critical" in s.lower() for s in report.focus_suggestions)

    def test_empty_portfolio(self):
        report = self.coordinator.generate_report("user", [])
        assert report.total_repos == 0
        assert report.focus_suggestions == []

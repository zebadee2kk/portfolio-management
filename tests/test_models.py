"""Tests for portfolio_manager.models."""

from datetime import datetime, timezone

from portfolio_manager.models import (
    PortfolioReport,
    PriorityLevel,
    PriorityScore,
    Repository,
)


def _make_repo(**kwargs) -> Repository:
    defaults = dict(
        name="test-repo",
        full_name="user/test-repo",
        url="https://api.github.com/repos/user/test-repo",
        html_url="https://github.com/user/test-repo",
    )
    defaults.update(kwargs)
    return Repository(**defaults)


class TestRepository:
    def test_defaults(self):
        repo = _make_repo()
        assert repo.stars == 0
        assert repo.forks == 0
        assert repo.open_issues == 0
        assert repo.is_fork is False
        assert repo.is_archived is False
        assert repo.is_private is False

    def test_days_since_push_none_when_no_pushed_at(self):
        repo = _make_repo()
        assert repo.days_since_push is None

    def test_days_since_push_recent(self):
        now = datetime.now(tz=timezone.utc)
        repo = _make_repo(pushed_at=now)
        assert repo.days_since_push == 0

    def test_is_active_recent_push(self):
        now = datetime.now(tz=timezone.utc)
        repo = _make_repo(pushed_at=now)
        assert repo.is_active is True

    def test_is_active_stale(self):
        old = datetime(2020, 1, 1, tzinfo=timezone.utc)
        repo = _make_repo(pushed_at=old)
        assert repo.is_active is False

    def test_is_active_no_push(self):
        repo = _make_repo()
        assert repo.is_active is False


class TestPriorityScore:
    def test_archived_level(self):
        score = PriorityScore(
            total=0.0,
            activity_score=0.0,
            engagement_score=0.0,
            health_score=0.0,
            recency_score=0.0,
            level=PriorityLevel.ARCHIVED,
        )
        assert score.level == PriorityLevel.ARCHIVED


class TestPortfolioReport:
    def test_defaults(self):
        report = PortfolioReport(owner="user")
        assert report.total_repos == 0
        assert report.prioritized == []
        assert report.languages == {}
        assert report.top_topics == []

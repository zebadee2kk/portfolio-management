"""Tests for portfolio_manager.prioritizer."""

from datetime import datetime, timedelta, timezone

from portfolio_manager.models import PriorityLevel, Repository
from portfolio_manager.prioritizer import ProjectPrioritizer


def _repo(
    name: str = "repo",
    *,
    stars: int = 0,
    forks: int = 0,
    open_issues: int = 0,
    days_since_push: int = 0,
    days_old: int = 30,
    is_archived: bool = False,
    topics: list[str] | None = None,
    description: str | None = None,
) -> Repository:
    now = datetime.now(tz=timezone.utc)
    pushed_at = now - timedelta(days=days_since_push)
    created_at = now - timedelta(days=days_old)
    return Repository(
        name=name,
        full_name=f"user/{name}",
        url=f"https://api.github.com/repos/user/{name}",
        html_url=f"https://github.com/user/{name}",
        stars=stars,
        forks=forks,
        open_issues=open_issues,
        pushed_at=pushed_at,
        created_at=created_at,
        is_archived=is_archived,
        topics=topics or [],
        description=description,
    )


class TestProjectPrioritizer:
    def setup_method(self):
        self.prioritizer = ProjectPrioritizer()

    def test_active_repo_scores_higher_than_stale(self):
        active = _repo("active", days_since_push=1)
        stale = _repo("stale", days_since_push=300)
        results = self.prioritizer.prioritize([stale, active])
        assert results[0].repo.name == "active"
        assert results[1].repo.name == "stale"

    def test_archived_repo_scores_zero(self):
        archived = _repo("archived", is_archived=True)
        results = self.prioritizer.prioritize([archived])
        assert results[0].score.total == 0.0
        assert results[0].score.level == PriorityLevel.ARCHIVED

    def test_popular_repo_scores_higher_than_empty(self):
        popular = _repo("popular", stars=500, days_since_push=10)
        empty = _repo("empty", stars=0, days_since_push=10)
        results = self.prioritizer.prioritize([empty, popular])
        assert results[0].repo.name == "popular"

    def test_priority_levels(self):
        # A freshly pushed, highly starred repo should be CRITICAL
        top = _repo("top", stars=1000, days_since_push=1, open_issues=5)
        result = self.prioritizer._score_repo(top)
        assert result.score.level == PriorityLevel.CRITICAL

        # A very old, low-activity repo should be LOW
        low = _repo("low", stars=0, days_since_push=364)
        result_low = self.prioritizer._score_repo(low)
        assert result_low.score.level in (PriorityLevel.LOW, PriorityLevel.MEDIUM)

    def test_suggested_actions_stale_repo(self):
        stale = _repo("stale", days_since_push=200)
        result = self.prioritizer._score_repo(stale)
        assert any("stale" in action.lower() for action in result.suggested_actions)

    def test_suggested_actions_no_description(self):
        repo = _repo("no-desc", description=None)
        result = self.prioritizer._score_repo(repo)
        assert any("description" in action.lower() for action in result.suggested_actions)

    def test_suggested_actions_no_topics(self):
        repo = _repo("no-topics", topics=[])
        result = self.prioritizer._score_repo(repo)
        assert any("topic" in action.lower() for action in result.suggested_actions)

    def test_prioritize_empty_list(self):
        assert self.prioritizer.prioritize([]) == []

    def test_scores_are_bounded(self):
        """All scores must be in [0, 100]."""
        repos = [
            _repo("a", stars=0, days_since_push=400),
            _repo("b", stars=10000, days_since_push=0, open_issues=100),
        ]
        for pr in self.prioritizer.prioritize(repos):
            assert 0.0 <= pr.score.total <= 100.0

"""Unit tests for src/health_scorer.py."""

from __future__ import annotations

import pytest

from src.health_scorer import RepoMetrics, calculate_health_score, grade_from_score


class TestCalculateHealthScore:
    def test_perfect_recent_healthy_repo(self):
        """Recently updated, no issues → score should be high (capped at 100)."""
        metrics = RepoMetrics(open_issues=0, days_since_update=1)
        score = calculate_health_score(metrics)
        # 100 + 10 (recent bonus) capped at 100
        assert score == 100.0

    def test_zero_issues_no_bonus(self):
        """No issues, updated 10 days ago → score = 100 (no stale penalty, no bonus)."""
        metrics = RepoMetrics(open_issues=0, days_since_update=10, has_license=True)
        score = calculate_health_score(metrics)
        assert score == 100.0

    def test_open_issues_reduce_score(self):
        """Each issue costs 2 points up to 40."""
        metrics = RepoMetrics(open_issues=5, days_since_update=1, has_license=True)
        # 100 - (5*2)=90, +10 recent bonus = 100 (capped)
        score = calculate_health_score(metrics)
        assert score == 100.0

    def test_open_issues_penalty_no_bonus(self):
        """Issues without recent activity bonus."""
        metrics = RepoMetrics(open_issues=5, days_since_update=20, has_license=True)
        # 100 - 10 (issues) = 90
        assert calculate_health_score(metrics) == 90.0

    def test_open_issues_max_penalty(self):
        """Issue penalty is capped at 40 regardless of count."""
        metrics = RepoMetrics(open_issues=100, days_since_update=20, has_license=True)
        # 100 - 40 (max penalty) = 60
        assert calculate_health_score(metrics) == 60.0

    def test_stale_penalty_applied(self):
        """Repos not updated in >30 days incur staleness penalty."""
        metrics = RepoMetrics(open_issues=0, days_since_update=50, has_license=True)
        # 100 - (50-30)*0.5 = 100 - 10 = 90
        assert calculate_health_score(metrics) == 90.0

    def test_stale_penalty_capped(self):
        """Staleness penalty is capped at 30."""
        metrics = RepoMetrics(open_issues=0, days_since_update=200, has_license=True)
        # 100 - 30 (max stale) = 70
        assert calculate_health_score(metrics) == 70.0

    def test_archived_repo_scores_zero(self):
        """Archived repos always score 0."""
        metrics = RepoMetrics(open_issues=0, days_since_update=0, is_archived=True)
        assert calculate_health_score(metrics) == 0.0

    def test_archived_ignores_other_metrics(self):
        """Archived check short-circuits before any other penalty."""
        metrics = RepoMetrics(
            open_issues=0,
            days_since_update=1,
            is_archived=True,
        )
        assert calculate_health_score(metrics) == 0.0

    def test_missing_readme_penalty(self):
        """Missing README reduces score by 10."""
        metrics = RepoMetrics(
            open_issues=0, days_since_update=20, has_readme=False, has_license=True
        )
        # 100 - 10 (no readme) = 90
        assert calculate_health_score(metrics) == 90.0

    def test_missing_license_penalty(self):
        """Missing licence reduces score by 5."""
        metrics = RepoMetrics(open_issues=0, days_since_update=20, has_license=False)
        # 100 - 5 = 95
        assert calculate_health_score(metrics) == 95.0

    def test_combined_penalties(self):
        """All penalties stack correctly."""
        metrics = RepoMetrics(
            open_issues=10,
            days_since_update=60,
            has_readme=False,
            has_license=False,
        )
        # 100 - 20 (issues) - 15 (stale: 30 days * 0.5) - 10 (no readme) - 5 (no lic) = 50
        assert calculate_health_score(metrics) == 50.0

    def test_score_never_below_zero(self):
        """Score floor is 0."""
        metrics = RepoMetrics(
            open_issues=100,
            days_since_update=1000,
            has_readme=False,
            has_license=False,
        )
        assert calculate_health_score(metrics) >= 0.0

    def test_score_never_above_100(self):
        """Score ceiling is 100."""
        metrics = RepoMetrics(open_issues=0, days_since_update=0)
        assert calculate_health_score(metrics) <= 100.0

    def test_recent_activity_bonus(self):
        """Updated within 7 days earns +10, capped at 100."""
        metrics = RepoMetrics(open_issues=5, days_since_update=3, has_license=True)
        # 100 - 10 (issues) + 10 (recent bonus) = 100 (capped)
        score = calculate_health_score(metrics)
        assert score == 100.0

    def test_recent_activity_bonus_visible(self):
        """Recent bonus pushes score above baseline when issues exist."""
        metrics = RepoMetrics(open_issues=10, days_since_update=5, has_license=True)
        # 100 - 20 (issues) + 10 (recent bonus) = 90
        assert calculate_health_score(metrics) == 90.0

    def test_return_type_is_float(self):
        metrics = RepoMetrics(open_issues=2, days_since_update=5)
        assert isinstance(calculate_health_score(metrics), float)


class TestGradeFromScore:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (100.0, "A"),
            (85.0, "A"),
            (84.9, "B"),
            (70.0, "B"),
            (69.9, "C"),
            (55.0, "C"),
            (54.9, "D"),
            (40.0, "D"),
            (39.9, "F"),
            (0.0, "F"),
        ],
    )
    def test_grade_boundaries(self, score, expected):
        assert grade_from_score(score) == expected

    def test_grade_returns_string(self):
        assert isinstance(grade_from_score(75.0), str)

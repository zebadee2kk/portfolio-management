"""Unit tests for src/github_scanner.py."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from src.github_scanner import GitHubScanner, _days_since

# ---------------------------------------------------------------------------
# _days_since helper
# ---------------------------------------------------------------------------


class TestDaysSince:
    def test_today_is_zero(self):
        assert _days_since(datetime.now(UTC)) == 0

    def test_yesterday_is_one(self):
        dt = datetime.now(UTC) - timedelta(days=1)
        assert _days_since(dt) == 1

    def test_thirty_days_ago(self):
        dt = datetime.now(UTC) - timedelta(days=30)
        assert _days_since(dt) == 30

    def test_naive_datetime_treated_as_utc(self):
        """Naive datetimes (no tzinfo) should be treated as UTC without raising."""
        naive = datetime.now().replace(tzinfo=None) - timedelta(days=5)  # intentionally naive
        result = _days_since(naive)
        assert result >= 4  # clock skew tolerance


# ---------------------------------------------------------------------------
# GitHubScanner construction
# ---------------------------------------------------------------------------


class TestGitHubScannerInit:
    def test_raises_without_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="GitHub token required"):
            GitHubScanner(token=None)

    def test_uses_provided_token(self):
        with patch("src.github_scanner.Github") as MockGithub:
            GitHubScanner(token="test-token")
            MockGithub.assert_called_once_with("test-token")

    def test_uses_github_token_env(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "env-token")
        with patch("src.github_scanner.Github") as MockGithub:
            GitHubScanner()
            MockGithub.assert_called_once_with("env-token")

    def test_uses_default_username(self, monkeypatch):
        monkeypatch.delenv("GITHUB_USERNAME", raising=False)
        with patch("src.github_scanner.Github"):
            scanner = GitHubScanner(token="tok")
            assert scanner._username == "zebadee2kk"

    def test_uses_username_env_var(self, monkeypatch):
        monkeypatch.setenv("GITHUB_USERNAME", "custom-user")
        with patch("src.github_scanner.Github"):
            scanner = GitHubScanner(token="tok")
            assert scanner._username == "custom-user"

    def test_uses_explicit_username(self, monkeypatch):
        monkeypatch.delenv("GITHUB_USERNAME", raising=False)
        with patch("src.github_scanner.Github"):
            scanner = GitHubScanner(token="tok", username="richco")
            assert scanner._username == "richco"


# ---------------------------------------------------------------------------
# scan_portfolio
# ---------------------------------------------------------------------------


class TestScanPortfolio:
    def _scanner(self, mock_github):
        with patch("src.github_scanner.Github", return_value=mock_github):
            return GitHubScanner(token="tok")

    def test_returns_list(self, mock_github):
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio()
        assert isinstance(results, list)

    def test_returns_all_repos_by_default(self, mock_github):
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio()
        assert len(results) == 2

    def test_filters_private_when_requested(self, mock_github, mock_repo, mock_stale_repo):
        mock_stale_repo.private = True
        mock_github.get_user.return_value.get_repos.return_value = [
            mock_repo,
            mock_stale_repo,
        ]
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio(include_private=False)
        assert all(not r.get("private", True) for r in results)

    def test_each_result_has_expected_keys(self, mock_github):
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio()
        for r in results:
            for key in ("name", "health_score", "health_grade", "open_issues"):
                assert key in r, f"Missing key: {key}"

    def test_github_api_error_returns_empty_list(self, mock_github):
        mock_github.get_user.side_effect = GithubException(403, "Forbidden")
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio()
        assert results == []

    def test_per_repo_error_included_as_error_entry(self, mock_github, mock_repo):
        bad_repo = MagicMock()
        bad_repo.full_name = "zebadee2kk/bad-repo"
        bad_repo.open_issues_count = 0
        # updated_at raises an exception when accessed
        type(bad_repo).updated_at = property(
            fget=lambda self: (_ for _ in ()).throw(Exception("API fail"))
        )
        mock_github.get_user.return_value.get_repos.return_value = [mock_repo, bad_repo]
        scanner = self._scanner(mock_github)
        results = scanner.scan_portfolio()
        error_entries = [r for r in results if "error" in r]
        assert len(error_entries) == 1


# ---------------------------------------------------------------------------
# scan_repo
# ---------------------------------------------------------------------------


class TestScanRepo:
    def _scanner(self, mock_github):
        with patch("src.github_scanner.Github", return_value=mock_github):
            return GitHubScanner(token="tok")

    def test_basic_depth(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="basic")
        assert "health_score" in result
        assert "name" in result

    def test_detailed_depth_adds_commits(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="detailed")
        assert "recent_commit_count" in result
        assert "license" in result

    def test_comprehensive_depth_adds_contributors(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="comprehensive")
        assert "contributor_count" in result
        assert "topics" in result

    def test_full_name_not_modified_when_slash_present(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        scanner.scan_repo("owner/test-repo", depth="basic")
        mock_github.get_repo.assert_called_with("owner/test-repo")

    def test_short_name_gets_username_prefix(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        scanner.scan_repo("test-repo", depth="basic")
        mock_github.get_repo.assert_called_with("zebadee2kk/test-repo")

    def test_invalid_depth_raises(self, mock_github):
        scanner = self._scanner(mock_github)
        with pytest.raises(ValueError, match="depth must be one of"):
            scanner.scan_repo("test-repo", depth="ultra")


# ---------------------------------------------------------------------------
# compare_repos
# ---------------------------------------------------------------------------


class TestCompareRepos:
    def _scanner(self, mock_github):
        with patch("src.github_scanner.Github", return_value=mock_github):
            return GitHubScanner(token="tok")

    def test_returns_list_with_one_entry_per_repo(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a", "repo-b"])
        assert len(results) == 2

    def test_each_entry_has_name(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a"], criteria=["issues"])
        assert results[0]["name"] == "repo-a"

    def test_health_criterion_included(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a"], criteria=["health"])
        assert "health" in results[0]["metrics"]

    def test_activity_criterion_included(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a"], criteria=["activity"])
        assert "activity" in results[0]["metrics"]

    def test_size_criterion_included(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a"], criteria=["size"])
        assert "size_kb" in results[0]["metrics"]

    def test_github_error_returns_error_entry(self, mock_github):
        mock_github.get_repo.side_effect = GithubException(404, "Not Found")
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["missing-repo"])
        assert "error" in results[0]

    def test_default_criteria_all_four(self, mock_github, mock_repo):
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        results = scanner.compare_repos(["repo-a"])
        metrics = results[0]["metrics"]
        for key in ("activity", "health", "open_issues", "size_kb"):
            assert key in metrics, f"Missing metric: {key}"


# ---------------------------------------------------------------------------
# _basic_dict / _detailed_dict / _comprehensive_dict
# ---------------------------------------------------------------------------


class TestScannerDicts:
    def _scanner(self, mock_github):
        with patch("src.github_scanner.Github", return_value=mock_github):
            return GitHubScanner(token="tok")

    def test_archived_repo_scores_zero(self, mock_github, mock_archived_repo):
        mock_github.get_repo.return_value = mock_archived_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("archived-repo", depth="basic")
        assert result["health_score"] == 0.0
        assert result["health_grade"] == "F"

    def test_commit_api_error_graceful(self, mock_github, mock_repo):
        mock_repo.get_commits.side_effect = GithubException(500, "Server error")
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="detailed")
        assert result["recent_commit_count"] is None

    def test_contributors_api_error_graceful(self, mock_github, mock_repo):
        mock_repo.get_contributors.side_effect = GithubException(500, "Server error")
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="comprehensive")
        assert result["contributor_count"] is None

    def test_topics_api_error_graceful(self, mock_github, mock_repo):
        mock_repo.get_topics.side_effect = GithubException(500, "Server error")
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="comprehensive")
        assert result["topics"] == []

    def test_contents_api_error_graceful(self, mock_github, mock_repo):
        mock_repo.get_contents.side_effect = GithubException(500, "Server error")
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="comprehensive")
        assert result["root_files"] == []
        assert result["has_readme"] is None

    def test_empty_commits_list(self, mock_github, mock_repo):
        mock_repo.get_commits.return_value = []
        mock_github.get_repo.return_value = mock_repo
        scanner = self._scanner(mock_github)
        result = scanner.scan_repo("test-repo", depth="detailed")
        assert result["last_commit_date"] is None
        assert result["recent_commit_count"] == 0

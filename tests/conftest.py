"""Shared pytest fixtures for the portfolio-management test suite."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Datetime helpers
# ---------------------------------------------------------------------------


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_days_ago(n: int) -> datetime:
    from datetime import timedelta

    return utc_now() - timedelta(days=n)


# ---------------------------------------------------------------------------
# GitHub mock fixtures
# ---------------------------------------------------------------------------


def _make_mock_repo(
    name: str = "zebadee2kk/test-repo",
    open_issues: int = 3,
    days_old: int = 10,
    private: bool = False,
    archived: bool = False,
    language: str = "Python",
    description: str = "Test repo",
    stars: int = 0,
    forks: int = 0,
    size: int = 512,
    has_license: bool = True,
) -> MagicMock:
    """Build a minimal PyGithub Repository mock."""
    repo = MagicMock()
    repo.full_name = name
    repo.description = description
    repo.private = private
    repo.archived = archived
    repo.language = language
    repo.open_issues_count = open_issues
    repo.stargazers_count = stars
    repo.forks_count = forks
    repo.size = size
    repo.updated_at = utc_days_ago(days_old)

    # License mock
    if has_license:
        license_mock = MagicMock()
        license_mock.name = "MIT License"
        repo.license = license_mock
    else:
        repo.license = None

    # Commits mock
    commit_mock = MagicMock()
    commit_mock.commit.author.date = utc_days_ago(days_old)
    repo.get_commits.return_value = [commit_mock] * 5

    # Contributors mock
    repo.get_contributors.return_value = [MagicMock(), MagicMock()]

    # Topics mock
    repo.get_topics.return_value = ["python", "automation"]

    # Root contents mock
    readme_file = MagicMock()
    readme_file.name = "README.md"
    readme_file.type = "file"
    license_file = MagicMock()
    license_file.name = "LICENSE"
    license_file.type = "file"
    repo.get_contents.return_value = [readme_file, license_file]

    return repo


@pytest.fixture
def mock_repo() -> MagicMock:
    """A healthy, recently-updated mock repo."""
    return _make_mock_repo()


@pytest.fixture
def mock_stale_repo() -> MagicMock:
    """A stale repo — no updates in 60 days, many issues."""
    return _make_mock_repo(
        name="zebadee2kk/stale-repo",
        days_old=60,
        open_issues=15,
    )


@pytest.fixture
def mock_archived_repo() -> MagicMock:
    return _make_mock_repo(
        name="zebadee2kk/archived-repo",
        archived=True,
        days_old=365,
    )


@pytest.fixture
def mock_github(mock_repo, mock_stale_repo):
    """A PyGithub Github instance mock returning two repos."""
    gh = MagicMock()
    user_mock = MagicMock()
    user_mock.get_repos.return_value = [mock_repo, mock_stale_repo]
    gh.get_user.return_value = user_mock
    gh.get_repo.return_value = mock_repo
    return gh


# ---------------------------------------------------------------------------
# Cache fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_cache_dir(tmp_path: Path) -> Path:
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir

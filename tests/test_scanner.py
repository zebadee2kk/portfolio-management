"""Tests for portfolio_manager.scanner."""

from unittest.mock import MagicMock

import httpx

from portfolio_manager.scanner import GitHubScanner

RAW_REPO = {
    "name": "my-repo",
    "full_name": "user/my-repo",
    "description": "A test repo",
    "url": "https://api.github.com/repos/user/my-repo",
    "html_url": "https://github.com/user/my-repo",
    "language": "Python",
    "topics": ["ai", "python"],
    "stargazers_count": 42,
    "forks_count": 3,
    "open_issues_count": 2,
    "fork": False,
    "archived": False,
    "private": False,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "pushed_at": "2024-06-01T00:00:00Z",
    "default_branch": "main",
    "size": 512,
}


class TestGitHubScannerParseRepo:
    def test_parse_repo_basic_fields(self):
        repo = GitHubScanner._parse_repo(RAW_REPO)
        assert repo.name == "my-repo"
        assert repo.full_name == "user/my-repo"
        assert repo.language == "Python"
        assert repo.stars == 42
        assert repo.forks == 3
        assert repo.open_issues == 2
        assert repo.topics == ["ai", "python"]
        assert repo.is_fork is False
        assert repo.is_archived is False
        assert repo.default_branch == "main"
        assert repo.size_kb == 512

    def test_parse_repo_dates(self):
        repo = GitHubScanner._parse_repo(RAW_REPO)
        assert repo.pushed_at is not None
        assert repo.pushed_at.year == 2024

    def test_parse_repo_missing_optional_fields(self):
        minimal = {
            "name": "minimal",
            "full_name": "user/minimal",
            "url": "https://api.github.com/repos/user/minimal",
            "html_url": "https://github.com/user/minimal",
        }
        repo = GitHubScanner._parse_repo(minimal)
        assert repo.description is None
        assert repo.language is None
        assert repo.topics == []
        assert repo.pushed_at is None


class TestGitHubScannerNextPage:
    def test_next_page_present(self):
        response = MagicMock(spec=httpx.Response)
        response.headers = {
            "Link": '<https://api.github.com/users/user/repos?page=2>; rel="next", '
                    '<https://api.github.com/users/user/repos?page=5>; rel="last"'
        }
        url = GitHubScanner._next_page(response)
        assert url == "https://api.github.com/users/user/repos?page=2"

    def test_next_page_absent(self):
        response = MagicMock(spec=httpx.Response)
        response.headers = {
            "Link": '<https://api.github.com/users/user/repos?page=4>; rel="last"'
        }
        url = GitHubScanner._next_page(response)
        assert url is None

    def test_next_page_no_link_header(self):
        response = MagicMock(spec=httpx.Response)
        response.headers = {}
        url = GitHubScanner._next_page(response)
        assert url is None


class TestGitHubScannerContextManager:
    def test_context_manager(self):
        with GitHubScanner() as scanner:
            assert scanner is not None
        # After __exit__ the client should be closed (no error raised)

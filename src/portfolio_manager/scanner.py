"""GitHub repository scanner using the GitHub REST API."""

from __future__ import annotations

import logging

import httpx

from portfolio_manager.models import Repository

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubScanner:
    """Scan a GitHub user or organisation for repository metadata.

    Args:
        token: Personal access token (PAT).  Unauthenticated requests are
               rate-limited to 60/hour; authenticated requests get 5 000/hour.
        per_page: Page size when listing repositories (max 100).
    """

    def __init__(self, token: str | None = None, per_page: int = 100) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=30.0,
        )
        self._per_page = per_page

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def scan_user(self, username: str) -> list[Repository]:
        """Return all public repositories for *username*."""
        return self._paginate(f"/users/{username}/repos", params={"type": "owner"})

    def scan_org(self, org: str) -> list[Repository]:
        """Return all public repositories for organisation *org*."""
        return self._paginate(f"/orgs/{org}/repos")

    def get_repo(self, owner: str, repo: str) -> Repository:
        """Fetch metadata for a single repository."""
        response = self._client.get(f"/repos/{owner}/{repo}")
        response.raise_for_status()
        return self._parse_repo(response.json())

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> GitHubScanner:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _paginate(self, path: str, params: dict | None = None) -> list[Repository]:
        """Follow GitHub's ``Link`` pagination and accumulate all results."""
        params = {**(params or {}), "per_page": self._per_page}
        results: list[Repository] = []
        url: str | None = path

        while url:
            response = self._client.get(url, params=params if url == path else None)
            response.raise_for_status()
            for raw in response.json():
                try:
                    results.append(self._parse_repo(raw))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Could not parse repo %s: %s", raw.get("full_name"), exc)

            # Follow GitHub pagination via the Link header
            url = self._next_page(response)

        return results

    @staticmethod
    def _next_page(response: httpx.Response) -> str | None:
        """Extract the 'next' URL from a GitHub Link header, if present."""
        link_header = response.headers.get("Link", "")
        for part in link_header.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                return part.split(";")[0].strip().strip("<>")
        return None

    @staticmethod
    def _parse_repo(data: dict) -> Repository:
        """Map a raw GitHub API payload to a :class:`Repository`."""
        from datetime import datetime

        def _parse_dt(value: str | None) -> datetime | None:
            if not value:
                return None
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return Repository(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            url=data.get("url", ""),
            html_url=data.get("html_url", ""),
            language=data.get("language"),
            topics=data.get("topics", []),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            is_fork=data.get("fork", False),
            is_archived=data.get("archived", False),
            is_private=data.get("private", False),
            created_at=_parse_dt(data.get("created_at")),
            updated_at=_parse_dt(data.get("updated_at")),
            pushed_at=_parse_dt(data.get("pushed_at")),
            default_branch=data.get("default_branch", "main"),
            size_kb=data.get("size", 0),
        )

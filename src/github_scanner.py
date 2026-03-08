"""GitHub portfolio scanning logic.

Wraps PyGithub calls and normalises raw repo objects into plain dicts
that MCP tools and the nightly workflow can consume directly.
All external calls are guarded; errors are logged and the affected
repo is returned with an ``error`` field rather than crashing the scan.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from github import Github, GithubException

from src.health_scorer import RepoMetrics, calculate_health_score, grade_from_score

logger = logging.getLogger(__name__)

# Default GitHub username — overridden by GITHUB_USERNAME env var
DEFAULT_GITHUB_USERNAME = "zebadee2kk"

# Number of recent commits to fetch for activity metrics
_COMMIT_SAMPLE_SIZE = 10


class GitHubScanner:
    """Scans one or more repositories and returns structured metrics.

    Args:
        token:    GitHub personal access token.  Defaults to the
                  ``GITHUB_TOKEN`` environment variable.
        username: GitHub username / org to scan.  Defaults to
                  ``GITHUB_USERNAME`` env var or ``zebadee2kk``.
    """

    def __init__(
        self,
        token: str | None = None,
        username: str | None = None,
    ) -> None:
        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if not resolved_token:
            raise ValueError(
                "GitHub token required: pass token= or set GITHUB_TOKEN env var"
            )
        self._gh = Github(resolved_token)
        self._username: str = (
            username
            or os.getenv("GITHUB_USERNAME")
            or DEFAULT_GITHUB_USERNAME
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan_portfolio(self, include_private: bool = True) -> list[dict[str, Any]]:
        """Scan every repository owned by the configured user.

        Args:
            include_private: When ``False``, skip private repos.

        Returns:
            List of repo dicts (see :meth:`_basic_dict`).
        """
        try:
            user = self._gh.get_user(self._username)
            repos = list(user.get_repos())
        except GithubException as exc:
            logger.error("GitHub API error listing repos: %s", exc)
            return []

        if not include_private:
            repos = [r for r in repos if not r.private]

        results: list[dict[str, Any]] = []
        for repo in repos:
            try:
                results.append(self._basic_dict(repo))
            except Exception as exc:  # noqa: BLE001 — broad catch per-repo intentional
                logger.warning("Failed to scan %s: %s", repo.full_name, exc)
                results.append({"name": repo.full_name, "error": str(exc)})

        logger.info("Portfolio scan complete: %d repos", len(results))
        return results

    def scan_repo(self, repo_name: str, depth: str = "detailed") -> dict[str, Any]:
        """Perform a single-repo scan at the requested depth.

        Args:
            repo_name: Short name (e.g. ``"control-tower"``) or full
                       ``"owner/repo"`` form.
            depth:     One of ``"basic"``, ``"detailed"``, ``"comprehensive"``.

        Returns:
            Dict with repo metrics.

        Raises:
            ValueError: If *depth* is not one of the accepted values.
            GithubException: On API errors.
        """
        valid_depths = {"basic", "detailed", "comprehensive"}
        if depth not in valid_depths:
            raise ValueError(f"depth must be one of {valid_depths}, got {depth!r}")

        full_name = repo_name if "/" in repo_name else f"{self._username}/{repo_name}"
        repo = self._gh.get_repo(full_name)

        if depth == "basic":
            return self._basic_dict(repo)
        if depth == "comprehensive":
            return self._comprehensive_dict(repo)
        return self._detailed_dict(repo)

    def compare_repos(
        self,
        repo_names: list[str],
        criteria: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Side-by-side comparison of multiple repositories.

        Args:
            repo_names: List of repo names (short or full form).
            criteria:   Subset of ``["activity", "health", "issues", "size"]``.
                        Defaults to all four.

        Returns:
            List of comparison dicts, one per repo.
        """
        criteria = criteria or ["activity", "health", "issues", "size"]
        results: list[dict[str, Any]] = []

        for name in repo_names:
            full_name = name if "/" in name else f"{self._username}/{name}"
            try:
                repo = self._gh.get_repo(full_name)
                entry: dict[str, Any] = {"name": name, "metrics": {}}

                if "activity" in criteria:
                    entry["metrics"]["activity"] = self._activity_metrics(repo)
                if "health" in criteria:
                    entry["metrics"]["health"] = self._health_dict(repo)
                if "issues" in criteria:
                    entry["metrics"]["open_issues"] = repo.open_issues_count
                if "size" in criteria:
                    entry["metrics"]["size_kb"] = repo.size

                results.append(entry)
            except GithubException as exc:
                logger.warning("Could not compare %s: %s", name, exc)
                results.append({"name": name, "error": str(exc)})

        return results

    # ------------------------------------------------------------------
    # Private helpers — repo object → dict
    # ------------------------------------------------------------------

    def _basic_dict(self, repo: Any) -> dict[str, Any]:
        """Return a minimal dict from a PyGithub Repo object."""
        days_since_update = _days_since(repo.updated_at)
        metrics = RepoMetrics(
            open_issues=repo.open_issues_count,
            days_since_update=days_since_update,
            is_archived=repo.archived,
        )
        score = calculate_health_score(metrics)
        return {
            "name": repo.full_name,
            "description": repo.description or "",
            "private": repo.private,
            "archived": repo.archived,
            "language": repo.language,
            "open_issues": repo.open_issues_count,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "size_kb": repo.size,
            "last_updated": repo.updated_at.isoformat(),
            "days_since_update": days_since_update,
            "health_score": score,
            "health_grade": grade_from_score(score),
        }

    def _detailed_dict(self, repo: Any) -> dict[str, Any]:
        """Extend basic dict with commit activity and licence info."""
        data = self._basic_dict(repo)
        data.update(self._activity_metrics(repo))
        data["license"] = repo.license.name if repo.license else None
        return data

    def _comprehensive_dict(self, repo: Any) -> dict[str, Any]:
        """Extend detailed dict with contributors, topics, and root files."""
        data = self._detailed_dict(repo)

        try:
            contributors = list(repo.get_contributors())
            data["contributor_count"] = len(contributors)
        except GithubException as exc:
            logger.debug("Could not fetch contributors for %s: %s", repo.full_name, exc)
            data["contributor_count"] = None

        try:
            data["topics"] = repo.get_topics()
        except GithubException as exc:
            logger.debug("Could not fetch topics for %s: %s", repo.full_name, exc)
            data["topics"] = []

        try:
            contents = repo.get_contents("")
            root_files = [c.name for c in contents if c.type == "file"]
            data["root_files"] = root_files
            data["has_readme"] = any(
                f.lower() in ("readme.md", "readme.rst", "readme.txt", "readme")
                for f in root_files
            )
            data["has_license"] = any(
                f.lower().startswith("license") for f in root_files
            )
        except GithubException as exc:
            logger.debug("Could not fetch root contents for %s: %s", repo.full_name, exc)
            data["root_files"] = []
            data["has_readme"] = None
            data["has_license"] = None

        return data

    def _activity_metrics(self, repo: Any) -> dict[str, Any]:
        """Return commit activity metrics."""
        try:
            commits = list(repo.get_commits()[:_COMMIT_SAMPLE_SIZE])
            last_commit_date = (
                commits[0].commit.author.date.isoformat() if commits else None
            )
            return {
                "recent_commit_count": len(commits),
                "last_commit_date": last_commit_date,
            }
        except GithubException as exc:
            logger.debug("Could not fetch commits for %s: %s", repo.full_name, exc)
            return {"recent_commit_count": None, "last_commit_date": None}

    def _health_dict(self, repo: Any) -> dict[str, Any]:
        """Return health score and grade."""
        days = _days_since(repo.updated_at)
        metrics = RepoMetrics(
            open_issues=repo.open_issues_count,
            days_since_update=days,
            is_archived=repo.archived,
        )
        score = calculate_health_score(metrics)
        return {"score": score, "grade": grade_from_score(score)}


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _days_since(dt: datetime) -> int:
    """Return the number of whole days between *dt* and now (UTC).

    Args:
        dt: A timezone-aware datetime.

    Returns:
        Non-negative integer.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    delta = datetime.now(UTC) - dt
    return max(0, delta.days)

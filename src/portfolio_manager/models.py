"""Data models for the Portfolio Manager."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class PriorityLevel(str, Enum):
    """Priority level for a repository."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVED = "archived"


class Repository(BaseModel):
    """Represents a GitHub repository with its key metadata."""

    name: str
    full_name: str
    description: str | None = None
    url: str
    html_url: str
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    is_fork: bool = False
    is_archived: bool = False
    is_private: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None
    default_branch: str = "main"
    size_kb: int = 0

    @property
    def days_since_push(self) -> int | None:
        """Return number of days since last push, or None if unknown."""
        if self.pushed_at is None:
            return None
        delta = datetime.now(tz=timezone.utc) - self.pushed_at.replace(tzinfo=timezone.utc)
        return delta.days

    @property
    def is_active(self) -> bool:
        """Return True if the repo had a push in the last 90 days."""
        days = self.days_since_push
        return days is not None and days <= 90


class PriorityScore(BaseModel):
    """Detailed breakdown of a repository's priority score."""

    total: float = Field(..., description="Overall priority score (0-100)")
    activity_score: float = Field(..., description="Score based on recent activity")
    engagement_score: float = Field(..., description="Score based on stars/forks")
    health_score: float = Field(..., description="Score based on open issues vs activity")
    recency_score: float = Field(..., description="Score based on creation/update recency")
    level: PriorityLevel = Field(..., description="Human-readable priority level")


class PrioritizedRepo(BaseModel):
    """A repository paired with its computed priority score."""

    repo: Repository
    score: PriorityScore
    suggested_actions: list[str] = Field(default_factory=list)


class PortfolioReport(BaseModel):
    """A full portfolio report across all scanned repositories."""

    owner: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    total_repos: int = 0
    active_repos: int = 0
    stale_repos: int = 0
    archived_repos: int = 0
    prioritized: list[PrioritizedRepo] = Field(default_factory=list)
    languages: dict[str, int] = Field(default_factory=dict)
    top_topics: list[str] = Field(default_factory=list)
    focus_suggestions: list[str] = Field(default_factory=list)

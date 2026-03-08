"""Repository health scoring logic.

Produces a 0–100 score from raw repository metrics.
Kept separate from GitHub API calls so it can be unit-tested
without network access.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Scoring weights — tunable without changing logic
_OPEN_ISSUES_PENALTY_PER_ISSUE = 2.0
_OPEN_ISSUES_MAX_PENALTY = 40.0
_STALE_THRESHOLD_DAYS = 30
_STALE_PENALTY_PER_DAY = 0.5
_STALE_MAX_PENALTY = 30.0
_RECENT_ACTIVITY_BONUS_DAYS = 7
_RECENT_ACTIVITY_BONUS = 10.0
_NO_README_PENALTY = 10.0
_NO_LICENSE_PENALTY = 5.0
_SCORE_MIN = 0.0
_SCORE_MAX = 100.0


@dataclass
class RepoMetrics:
    """Flat metrics used for health scoring.

    All callers normalise GitHub API objects into this structure
    before scoring so the scorer has no PyGithub dependency.
    """

    open_issues: int
    days_since_update: int
    has_readme: bool = True
    has_license: bool = False
    is_archived: bool = False


def calculate_health_score(metrics: RepoMetrics) -> float:
    """Return a 0–100 health score for a repository.

    Higher is healthier. Penalties are applied for open issues,
    staleness, missing README/licence; bonus for recent activity.
    Archived repos score 0 immediately.

    Args:
        metrics: Flat snapshot of the repository's current state.

    Returns:
        Float in [0.0, 100.0].
    """
    if metrics.is_archived:
        logger.debug("Repo is archived — returning 0")
        return 0.0

    score = _SCORE_MAX

    # Penalty: open issues
    issue_penalty = min(
        metrics.open_issues * _OPEN_ISSUES_PENALTY_PER_ISSUE,
        _OPEN_ISSUES_MAX_PENALTY,
    )
    score -= issue_penalty

    # Penalty: staleness
    if metrics.days_since_update > _STALE_THRESHOLD_DAYS:
        excess_days = metrics.days_since_update - _STALE_THRESHOLD_DAYS
        stale_penalty = min(excess_days * _STALE_PENALTY_PER_DAY, _STALE_MAX_PENALTY)
        score -= stale_penalty

    # Penalty: missing docs
    if not metrics.has_readme:
        score -= _NO_README_PENALTY
    if not metrics.has_license:
        score -= _NO_LICENSE_PENALTY

    # Bonus: recent activity
    if metrics.days_since_update < _RECENT_ACTIVITY_BONUS_DAYS:
        score += _RECENT_ACTIVITY_BONUS

    return round(max(_SCORE_MIN, min(_SCORE_MAX, score)), 1)


def grade_from_score(score: float) -> str:
    """Map a numeric health score to a letter grade.

    Args:
        score: Value in [0, 100].

    Returns:
        One of 'A', 'B', 'C', 'D', 'F'.
    """
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"

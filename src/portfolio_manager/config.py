"""Configuration management for Portfolio Manager."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Runtime configuration, loaded from environment variables.

    Use :func:`from_env` to build an instance from the current environment.
    """

    github_token: str | None = None
    github_username: str | None = None
    default_per_page: int = 100

    @classmethod
    def from_env(cls) -> Config:
        """Read configuration from environment variables."""
        per_page_raw = os.getenv("PORTFOLIO_PER_PAGE", "100")
        try:
            per_page = int(per_page_raw)
        except ValueError:
            per_page = 100

        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            github_username=os.getenv("GITHUB_USERNAME"),
            default_per_page=per_page,
        )

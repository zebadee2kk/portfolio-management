"""Simple TTL file cache backed by JSON.

Scan results are expensive (GitHub API calls); caching avoids
re-scanning on every MCP query.  Cache files live in a directory
configured via the ``PORTFOLIO_CACHE_DIR`` environment variable
(default: ``/tmp/portfolio_cache``).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path("/tmp/portfolio_cache")  # noqa: S108 — intentional temp dir
DEFAULT_TTL_HOURS = 6


class FileCache:
    """JSON-backed file cache with per-entry TTL.

    Args:
        cache_dir:  Directory for cache files.  Created if absent.
        ttl_hours:  Entries older than this are considered stale.
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> None:
        env_dir = os.getenv("PORTFOLIO_CACHE_DIR")
        self._dir = Path(env_dir) if env_dir else (cache_dir or DEFAULT_CACHE_DIR)
        self._ttl = timedelta(hours=ttl_hours)
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Any | None:
        """Return cached value for *key*, or ``None`` if missing/expired.

        Args:
            key: Cache key (alphanumeric + underscores recommended).

        Returns:
            Deserialized value, or ``None``.
        """
        cache_file = self._path(key)
        if not cache_file.exists():
            logger.debug("Cache miss (absent): %s", key)
            return None

        try:
            entry = json.loads(cache_file.read_text(encoding="utf-8"))
            stored_at = datetime.fromisoformat(entry["stored_at"])
            if datetime.now(UTC) - stored_at > self._ttl:
                logger.debug("Cache miss (expired): %s", key)
                return None
            logger.debug("Cache hit: %s", key)
            return entry["value"]
        except (KeyError, ValueError, OSError) as exc:
            logger.warning("Cache read error for %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any) -> None:
        """Persist *value* under *key* with a timestamp.

        Args:
            key:   Cache key.
            value: JSON-serialisable value.
        """
        entry = {
            "stored_at": datetime.now(UTC).isoformat(),
            "value": value,
        }
        try:
            self._path(key).write_text(
                json.dumps(entry, default=str), encoding="utf-8"
            )
            logger.debug("Cache set: %s", key)
        except OSError as exc:
            logger.warning("Cache write error for %s: %s", key, exc)

    def invalidate(self, key: str) -> bool:
        """Delete a single cache entry.

        Args:
            key: Cache key to remove.

        Returns:
            ``True`` if the entry existed and was deleted.
        """
        cache_file = self._path(key)
        if cache_file.exists():
            cache_file.unlink()
            logger.debug("Cache invalidated: %s", key)
            return True
        return False

    def clear(self) -> int:
        """Delete all cache entries.

        Returns:
            Number of entries removed.
        """
        count = 0
        for f in self._dir.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except OSError:
                pass
        logger.debug("Cache cleared: %d entries removed", count)
        return count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _path(self, key: str) -> Path:
        # Sanitise key to a safe filename
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self._dir / f"{safe_key}.json"

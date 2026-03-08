"""Unit tests for src/cache.py."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from src.cache import FileCache


class TestFileCacheGet:
    def test_returns_none_for_missing_key(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        assert cache.get("nonexistent") is None

    def test_returns_stored_value(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("key1", {"hello": "world"})
        assert cache.get("key1") == {"hello": "world"}

    def test_returns_none_for_expired_entry(self, tmp_cache_dir):
        """An entry written more than ttl_hours ago should be treated as expired."""
        cache = FileCache(cache_dir=tmp_cache_dir, ttl_hours=1)
        # Write a cache file with a timestamp 2 hours in the past
        old_time = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        entry = {"stored_at": old_time, "value": "stale"}
        cache_file = tmp_cache_dir / "key2.json"
        cache_file.write_text(json.dumps(entry), encoding="utf-8")
        assert cache.get("key2") is None

    def test_returns_value_within_ttl(self, tmp_cache_dir):
        """Entry within TTL window should be returned."""
        cache = FileCache(cache_dir=tmp_cache_dir, ttl_hours=6)
        cache.set("key3", [1, 2, 3])
        assert cache.get("key3") == [1, 2, 3]

    def test_handles_corrupt_cache_file(self, tmp_cache_dir):
        """Corrupt JSON should return None without raising."""
        cache = FileCache(cache_dir=tmp_cache_dir)
        (tmp_cache_dir / "corrupt.json").write_text("NOT_JSON", encoding="utf-8")
        assert cache.get("corrupt") is None

    def test_handles_missing_stored_at_field(self, tmp_cache_dir):
        """File missing stored_at key should return None."""
        cache = FileCache(cache_dir=tmp_cache_dir)
        (tmp_cache_dir / "badentry.json").write_text(
            json.dumps({"value": 42}), encoding="utf-8"
        )
        assert cache.get("badentry") is None


class TestFileCacheSet:
    def test_set_creates_file(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("mykey", "myvalue")
        assert (tmp_cache_dir / "mykey.json").exists()

    def test_set_stores_correct_value(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("data", {"a": 1})
        result = cache.get("data")
        assert result == {"a": 1}

    def test_set_overwrites_existing(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("k", "first")
        cache.set("k", "second")
        assert cache.get("k") == "second"

    def test_set_handles_non_serialisable_via_default_str(self, tmp_cache_dir):
        """Non-JSON-serialisable values fall back to str() — no exception raised."""
        cache = FileCache(cache_dir=tmp_cache_dir)
        # datetime objects are handled by default=str
        cache.set("dt_key", {"ts": datetime.now(UTC)})
        # Should not raise

    def test_set_sanitises_special_chars_in_key(self, tmp_cache_dir):
        """Keys with special chars are sanitised to safe filenames."""
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("owner/repo/detailed", "value")
        # Should create a file without slashes in the name
        files = list(tmp_cache_dir.glob("*.json"))
        assert len(files) == 1
        assert "/" not in files[0].name


class TestFileCacheInvalidate:
    def test_invalidate_existing_key(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("todelete", "bye")
        assert cache.invalidate("todelete") is True
        assert cache.get("todelete") is None

    def test_invalidate_nonexistent_key(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        assert cache.invalidate("ghost") is False

    def test_invalidate_does_not_affect_other_keys(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("keep", "yes")
        cache.set("remove", "no")
        cache.invalidate("remove")
        assert cache.get("keep") == "yes"


class TestFileCacheClear:
    def test_clear_removes_all_entries(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        for i in range(5):
            cache.set(f"key{i}", i)
        removed = cache.clear()
        assert removed == 5
        assert list(tmp_cache_dir.glob("*.json")) == []

    def test_clear_returns_zero_when_empty(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        assert cache.clear() == 0

    def test_clear_then_set_works(self, tmp_cache_dir):
        cache = FileCache(cache_dir=tmp_cache_dir)
        cache.set("k", "v")
        cache.clear()
        cache.set("new", "data")
        assert cache.get("new") == "data"


class TestFileCacheEnvDir:
    def test_uses_env_var_for_cache_dir(self, tmp_path, monkeypatch):
        env_dir = tmp_path / "env_cache"
        env_dir.mkdir()
        monkeypatch.setenv("PORTFOLIO_CACHE_DIR", str(env_dir))
        cache = FileCache()
        cache.set("env_key", "env_value")
        assert (env_dir / "env_key.json").exists()

    def test_creates_cache_dir_if_absent(self, tmp_path):
        new_dir = tmp_path / "new_subdir" / "cache"
        FileCache(cache_dir=new_dir)
        assert new_dir.exists()

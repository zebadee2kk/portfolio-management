"""Portfolio Scanner MCP Server.

Exposes portfolio-scanning capabilities as MCP tools so any MCP-compatible
AI client (Claude Desktop, control-tower, HeliOS, …) can query GitHub
portfolio health without custom integration code.

Usage (stdio transport — standard for local MCP servers):

    ~/.venv/bin/python mcp_servers/scanner_server.py

Claude Desktop config (~/.config/claude/claude_desktop_config.json):

    {
      "mcpServers": {
        "portfolio-scanner": {
          "command": "/home/derek/.venv/bin/python",
          "args": [
            "/home/derek/Documents/github-repos/portfolio-management/mcp_servers/scanner_server.py"
          ],
          "env": {
            "GITHUB_TOKEN": "<your-token>",
            "GITHUB_USERNAME": "zebadee2kk"
          }
        }
      }
    }

Environment variables:
    GITHUB_TOKEN        GitHub PAT with repo read access (required)
    GITHUB_USERNAME     GitHub username to scan (default: zebadee2kk)
    PORTFOLIO_CACHE_DIR Directory for scan cache (default: /tmp/portfolio_cache)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Allow running directly from repo root: python mcp_servers/scanner_server.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cache import FileCache  # noqa: E402
from src.github_scanner import GitHubScanner  # noqa: E402

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,  # MCP uses stdout for protocol; keep logs on stderr
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "portfolio-scanner",
    instructions=(
        "Scans GitHub repositories for health, activity, and metrics. "
        "Use scan_portfolio for a full view or scan_repo for a single repository."
    ),
)

_cache = FileCache()


def _get_scanner() -> GitHubScanner:
    """Construct a scanner from environment variables.

    Raises:
        RuntimeError: If GITHUB_TOKEN is not set.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable is required for portfolio-scanner"
        )
    return GitHubScanner(token=token)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def scan_portfolio(
    include_private: bool = True,
    force_refresh: bool = False,
) -> str:
    """Scan the entire GitHub portfolio and return health metrics for every repo.

    Results are cached for 6 hours.  Use force_refresh=True to bypass the cache.

    Args:
        include_private: Include private repositories in the scan.
        force_refresh:   Bypass cache and perform a fresh GitHub API scan.

    Returns:
        JSON string with scan metadata and per-repo health metrics.
    """
    cache_key = f"portfolio_scan_private_{include_private}"

    if not force_refresh:
        cached = _cache.get(cache_key)
        if cached is not None:
            logger.info("Returning cached portfolio scan")
            return json.dumps({"cached": True, **cached}, indent=2)

    logger.info("Starting portfolio scan (include_private=%s)", include_private)
    scanner = _get_scanner()
    results = scanner.scan_portfolio(include_private=include_private)

    payload = {
        "repo_count": len(results),
        "repos": results,
    }
    _cache.set(cache_key, payload)

    return json.dumps({"cached": False, **payload}, indent=2)


@mcp.tool()
def scan_repo(
    repo_name: str,
    depth: str = "detailed",
    force_refresh: bool = False,
) -> str:
    """Deep scan a single repository.

    Args:
        repo_name:     Short repo name (e.g. ``"control-tower"``) or full
                       ``"owner/repo"`` form.
        depth:         One of ``"basic"``, ``"detailed"``, ``"comprehensive"``.
                       Comprehensive also fetches contributors, topics, and
                       root-file manifest.
        force_refresh: Bypass cache for this repo.

    Returns:
        JSON string with repo metrics.
    """
    cache_key = f"repo_{repo_name}_{depth}"

    if not force_refresh:
        cached = _cache.get(cache_key)
        if cached is not None:
            logger.info("Returning cached scan for %s", repo_name)
            return json.dumps({"cached": True, **cached}, indent=2)

    logger.info("Scanning repo %s (depth=%s)", repo_name, depth)
    scanner = _get_scanner()
    result = scanner.scan_repo(repo_name=repo_name, depth=depth)

    _cache.set(cache_key, result)
    return json.dumps({"cached": False, **result}, indent=2)


@mcp.tool()
def compare_repos(
    repo_names: list[str],
    criteria: list[str] | None = None,
) -> str:
    """Compare multiple repositories side by side.

    Args:
        repo_names: List of short repo names or ``"owner/repo"`` strings.
        criteria:   Which metrics to compare.  Defaults to all of:
                    ``["activity", "health", "issues", "size"]``.

    Returns:
        JSON array of comparison dicts, one per repo.
    """
    if not repo_names:
        return json.dumps({"error": "repo_names must not be empty"})

    criteria = criteria or ["activity", "health", "issues", "size"]
    logger.info("Comparing %d repos: %s", len(repo_names), repo_names)

    scanner = _get_scanner()
    results = scanner.compare_repos(repo_names=repo_names, criteria=criteria)
    return json.dumps(results, indent=2)


@mcp.tool()
def invalidate_cache(repo_name: str | None = None) -> str:
    """Invalidate cached scan results.

    Args:
        repo_name: If provided, invalidate only this repo's cache entries.
                   If omitted, clear the entire portfolio cache.

    Returns:
        JSON confirmation message.
    """
    if repo_name:
        removed = 0
        for depth in ("basic", "detailed", "comprehensive"):
            if _cache.invalidate(f"repo_{repo_name}_{depth}"):
                removed += 1
        return json.dumps({"cleared": removed, "target": repo_name})

    count = _cache.clear()
    return json.dumps({"cleared": count, "target": "all"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting portfolio-scanner MCP server (stdio transport)")
    mcp.run(transport="stdio")

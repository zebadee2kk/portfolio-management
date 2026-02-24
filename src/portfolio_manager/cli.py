"""Command-line interface for Portfolio Manager."""

from __future__ import annotations

import argparse
import json
import sys

from portfolio_manager.config import Config
from portfolio_manager.coordinator import RepoCoordinator
from portfolio_manager.prioritizer import ProjectPrioritizer
from portfolio_manager.scanner import GitHubScanner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portfolio-manager",
        description="AI-powered GitHub portfolio management — repo scanning, "
        "prioritisation, and cross-repo coordination.",
    )
    parser.add_argument(
        "--token",
        metavar="GITHUB_TOKEN",
        help="GitHub personal access token (overrides GITHUB_TOKEN env var).",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # scan ----------------------------------------------------------------
    scan_p = sub.add_parser("scan", help="Scan repositories for a GitHub user or org.")
    scan_p.add_argument("owner", help="GitHub username or organisation to scan.")
    scan_p.add_argument(
        "--type",
        dest="owner_type",
        choices=["user", "org"],
        default="user",
        help="Whether *owner* is a user or an organisation (default: user).",
    )

    # report ---------------------------------------------------------------
    report_p = sub.add_parser(
        "report",
        help="Generate a full prioritised portfolio report.",
    )
    report_p.add_argument("owner", help="GitHub username or organisation to report on.")
    report_p.add_argument(
        "--type",
        dest="owner_type",
        choices=["user", "org"],
        default="user",
        help="Whether *owner* is a user or an organisation (default: user).",
    )

    return parser


def _get_token(args: argparse.Namespace, config: Config) -> str | None:
    return args.token or config.github_token


def cmd_scan(args: argparse.Namespace, config: Config) -> int:
    token = _get_token(args, config)
    with GitHubScanner(token=token) as scanner:
        repos = (
            scanner.scan_user(args.owner)
            if args.owner_type == "user"
            else scanner.scan_org(args.owner)
        )

    if args.output == "json":
        print(json.dumps([r.model_dump(mode="json") for r in repos], indent=2))
    else:
        print(f"Found {len(repos)} repositories for '{args.owner}':\n")
        for repo in repos:
            status = "🗄 archived" if repo.is_archived else ("✅ active" if repo.is_active else "💤 stale")
            print(f"  {repo.full_name:50s}  {status}  ⭐{repo.stars}")
    return 0


def cmd_report(args: argparse.Namespace, config: Config) -> int:
    token = _get_token(args, config)
    with GitHubScanner(token=token) as scanner:
        repos = (
            scanner.scan_user(args.owner)
            if args.owner_type == "user"
            else scanner.scan_org(args.owner)
        )

    prioritizer = ProjectPrioritizer()
    prioritized = prioritizer.prioritize(repos)

    coordinator = RepoCoordinator()
    report = coordinator.generate_report(args.owner, prioritized)

    if args.output == "json":
        print(report.model_dump_json(indent=2))
        return 0

    # Text output
    print(f"\n📊 Portfolio Report — {report.owner}")
    print(f"   Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Total: {report.total_repos} repos  "
          f"({report.active_repos} active, {report.stale_repos} stale, "
          f"{report.archived_repos} archived)\n")

    if report.focus_suggestions:
        print("💡 Focus Suggestions:")
        for suggestion in report.focus_suggestions:
            print(f"   {suggestion}")
        print()

    print("📋 Prioritised Repositories:")
    print(f"  {'Repository':<45} {'Priority':<10} {'Score':>6}  Actions")
    print("  " + "-" * 90)
    for pr in report.prioritized:
        level_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "archived": "⚫",
        }.get(pr.score.level.value, "⚪")
        actions_preview = pr.suggested_actions[0] if pr.suggested_actions else ""
        print(
            f"  {pr.repo.full_name:<45} "
            f"{level_emoji} {pr.score.level.value:<8} "
            f"{pr.score.total:>6.1f}  {actions_preview[:50]}"
        )

    if report.languages:
        print("\n🗺  Languages:")
        for lang, count in list(report.languages.items())[:8]:
            print(f"   {lang}: {count}")

    return 0


def main(argv: list[str] | None = None) -> int:
    config = Config.from_env()
    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "scan": cmd_scan,
        "report": cmd_report,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    try:
        return handler(args, config)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

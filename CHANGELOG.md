# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.1.0] — 2026-02-24

### Added
- Initial project scaffold (`src/portfolio_manager/`, `tests/`, `docs/`)
- `models.py` — Pydantic data models: `Repository`, `PriorityScore`, `PrioritizedRepo`, `PortfolioReport`, `PriorityLevel`
- `scanner.py` — `GitHubScanner` class for paginated GitHub REST API scanning (user & org)
- `prioritizer.py` — `ProjectPrioritizer` with deterministic 0–100 scoring (activity, engagement, health, recency)
- `coordinator.py` — `RepoCoordinator` for cross-repo aggregation and portfolio report generation
- `config.py` — environment-variable-based `Config` dataclass
- `cli.py` — `portfolio-manager` CLI with `scan` and `report` sub-commands (text + JSON output)
- `pyproject.toml` — project metadata, tool configuration (ruff, black, mypy, pytest)
- `requirements.txt`, `.env.example`, `.gitignore`
- `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`
- Full pytest test suite covering models, scanner, prioritiser, and coordinator

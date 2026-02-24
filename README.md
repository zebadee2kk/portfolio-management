# portfolio-management 📊

> **AI-powered GitHub portfolio management system — automated repo scanning, project prioritisation, and cross-repo coordination.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🌟 What Is This?

`portfolio-management` is a CLI tool and Python library that helps you stay on top of your GitHub repositories at scale.  It:

1. **Scans** all repositories for a user or organisation via the GitHub REST API.
2. **Prioritises** repos using a transparent, deterministic scoring model (activity, engagement, health, recency).
3. **Coordinates** cross-repo insights — highlighting active projects, stale ones, missing metadata, and what to focus on next.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- A [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) (recommended; unauthenticated access is heavily rate-limited)

### Installation

```bash
# Clone the repo
git clone https://github.com/zebadee2kk/portfolio-management.git
cd portfolio-management

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install (editable mode for development)
pip install -e ".[dev]"

# Copy and populate environment variables
cp .env.example .env
# Edit .env and set GITHUB_TOKEN and GITHUB_USERNAME
```

### Usage

```bash
# Scan all repos for a user
portfolio-manager scan zebadee2kk

# Generate a full prioritised portfolio report (text)
portfolio-manager report zebadee2kk

# Same but as JSON (useful for piping into other tools)
portfolio-manager --output json report zebadee2kk

# Scan an organisation
portfolio-manager scan my-org --type org

# Use a specific token inline
portfolio-manager --token ghp_xxx report zebadee2kk
```

### Example Output

```
📊 Portfolio Report — zebadee2kk
   Generated: 2026-02-24 12:00 UTC
   Total: 12 repos  (8 active, 3 stale, 1 archived)

💡 Focus Suggestions:
   🔴 Critical priority: zebadee2kk/ai-powertools. Focus here first.
   🟠 High priority: zebadee2kk/zebra-ecosystem. Schedule work soon.
   📝 2 repos lack descriptions — add them for discoverability.

📋 Prioritised Repositories:
  Repository                                    Priority    Score  Actions
  ------------------------------------------------------------------------------------------
  zebadee2kk/ai-powertools                      🔴 critical  82.3  High open-issue count…
  zebadee2kk/zebra-ecosystem                    🟠 high      65.1
  …
```

---

## 🏗️ Architecture

```
portfolio-management/
├── src/portfolio_manager/
│   ├── __init__.py        # Package metadata
│   ├── models.py          # Pydantic data models (Repository, PriorityScore, …)
│   ├── scanner.py         # GitHub API repo scanner (GitHubScanner)
│   ├── prioritizer.py     # Deterministic priority scoring (ProjectPrioritizer)
│   ├── coordinator.py     # Cross-repo reporting (RepoCoordinator)
│   ├── config.py          # Environment-based configuration
│   └── cli.py             # Argparse CLI entry point
├── tests/                 # pytest test suite
├── docs/                  # Extended documentation
├── .env.example           # Environment variable template
├── pyproject.toml         # Project metadata and tool configuration
└── requirements.txt       # Pinned development dependencies
```

### Priority Scoring

Repositories are scored on a **0–100 scale** across four factors:

| Factor | Max pts | Description |
|---|---|---|
| **Activity** | 40 | Days since last push (linear decay, full score at 0 days → 0 at 365 days) |
| **Engagement** | 30 | Stars + forks (logarithmic scale) |
| **Health** | 20 | Open issues × recent activity |
| **Recency** | 10 | Age of the repo (newer = slightly higher) |

Priority levels: `CRITICAL` (≥70), `HIGH` (≥50), `MEDIUM` (≥25), `LOW` (<25), `ARCHIVED`.

---

## 🛠️ Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Format
black .

# Type check
mypy src/
```

---

## 📄 Roadmap

See [ROADMAP.md](ROADMAP.md) for the planned milestones.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🛡️ Security

See [SECURITY.md](SECURITY.md).

---

## 📄 License

MIT — see [LICENSE](LICENSE).

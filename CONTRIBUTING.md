# Contributing to portfolio-management 🤝

Thank you for your interest in contributing!

## 🌿 Branching Strategy

- **`main`**: Always stable, production-ready.
- **`feature/[name]`**: New features (e.g., `feature/sqlite-cache`).
- **`fix/[issue]`**: Bug fixes (e.g., `fix/pagination-loop`).
- **`research/[topic]`**: Exploratory branches.

## 🔄 Development Workflow

```bash
# Fork & clone
git clone https://github.com/zebadee2kk/portfolio-management.git
cd portfolio-management

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Create a feature branch
git checkout -b feature/my-feature

# Make changes, then:
pytest            # tests must pass
ruff check .      # lint must pass
black .           # format
```

## ✅ Handover Checklist

Before opening a PR:

- [ ] `pytest` passes
- [ ] `ruff check .` passes
- [ ] `black --check .` passes
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] New public functions have docstrings and type hints

## 📝 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add SQLite caching for scan results`
- `fix: handle missing Link header in pagination`
- `docs: update README quick-start section`
- `refactor: extract scoring weights to constants`

## 🤖 AI-to-Human Handover

If an AI agent completes a task it MUST:
- Summarise technical decisions made.
- List any new dependencies added.
- Provide a "What's Next" section for the human reviewer.

---

*Happy coding!* 🚀

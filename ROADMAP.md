# Roadmap 🗺️

**Vision:** A fully automated, AI-assisted GitHub portfolio management system that gives developers clear, actionable insight into their entire codebase at a glance.

---

## ✅ Phase 0 — Foundation (current)

- [x] Project scaffold (`src/`, `tests/`, `docs/`)
- [x] Core data models (`Repository`, `PriorityScore`, `PortfolioReport`)
- [x] GitHub repo scanner (`GitHubScanner` — user & org pagination)
- [x] Deterministic project prioritiser (`ProjectPrioritizer`)
- [x] Cross-repo coordinator & portfolio report (`RepoCoordinator`)
- [x] CLI entry point (`scan`, `report` commands, text + JSON output)
- [x] Test suite (models, scanner, prioritiser, coordinator)
- [x] `pyproject.toml`, `.gitignore`, `.env.example`, `requirements.txt`

---

## 🔜 Phase 1 — Enrichment & Persistence

- [ ] Cache scan results locally (SQLite) to avoid redundant API calls
- [ ] Persist historical snapshots for trend analysis (is a repo getting more or less active?)
- [ ] `diff` command — compare two snapshots and highlight changes
- [ ] Support GitHub App authentication (higher rate limits)
- [ ] Extended repo metadata: CI status, dependabot alerts, code frequency

---

## 🔜 Phase 2 — AI-Assisted Prioritisation

- [ ] Plug in an LLM (via `ai-powertools` router) for natural-language priority explanations
- [ ] Topic-cluster analysis: automatically group related repos
- [ ] Dependency graph: detect which repos import/depend on each other
- [ ] README quality scoring (length, sections, badges, examples)
- [ ] `suggest` command — ask the AI "what should I work on this week?"

---

## 🔜 Phase 3 — Cross-Repo Coordination

- [ ] Issue cross-referencing: surface issues that block multiple repos
- [ ] Milestone alignment: view open milestones across all repos on one page
- [ ] PR overview: pending reviews and stale PRs across the portfolio
- [ ] Automated weekly digest (email / Slack / Discord)

---

## 🔜 Phase 4 — Dashboard & Integrations

- [ ] Terminal UI (TUI) using `textual` for interactive portfolio browsing
- [ ] Export to GitHub Pages / static HTML report
- [ ] Webhook listener to update scores on push events in real time
- [ ] Integration with `zebra-ecosystem` cost tracking

---

> **Current status**: Phase 0 complete — foundational scanning, scoring, and CLI working.

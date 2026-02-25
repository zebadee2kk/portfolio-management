# Model Context Protocol (MCP) Integration Plan for Portfolio Management

**Date:** 2026-02-25  
**Status:** Research & Planning Phase  
**Priority:** Medium-High  
**Owner:** Project Manager / Data Architecture Lead

---

## Executive Summary

Portfolio Management is your AI-powered GitHub portfolio management system for automated repo scanning, project prioritization, and cross-repo coordination. MCP enables this system to expose portfolio analytics, scanning capabilities, and recommendation engines as standardized tools that any AI agent can consume, transforming it from a standalone analytics tool into a queryable intelligence layer for your entire ecosystem.

---

## What is MCP?

MCP (Model Context Protocol) is an open standard by Anthropic providing a universal interface for AI applications to access tools and data sources. For Portfolio Management, this means exposing portfolio insights through a consistent API that works across all your AI agents.

**Key Benefits for Portfolio Management:**
- AI-queryable portfolio analytics
- Standardized scanning and assessment interface
- Natural language access to prioritization logic
- Integration point for Control Tower coordination

**MCP Resources:**
- Official Python SDK: https://github.com/modelcontextprotocol/python-sdk (21,827 stars)
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk (11,675 stars)
- Server Examples: https://github.com/modelcontextprotocol/servers
- Documentation: https://modelcontextprotocol.io

---

## How MCP Benefits Portfolio Management

### 1. AI-Queryable Repository Scanning

**Current Challenge:**  
Scanning 9 public + 6 private repos to assess status, dependencies, and health requires manual execution of scripts or periodic batch jobs.

**MCP Solution:**  
Create `portfolio-scanner-server` exposing:
- `scan_portfolio(include_private)` - Full portfolio analysis
- `scan_repo(repo_name, depth)` - Deep scan of specific repository
- `compare_repos(repo_list, criteria)` - Side-by-side comparison
- `detect_anomalies(timeframe)` - Find unusual patterns (abandoned repos, spike in issues)

**Value:**  
- AI agents can trigger scans on-demand: "Scan my portfolio and show stale projects"
- Real-time analysis instead of waiting for scheduled jobs
- Consistent scanning interface for all downstream consumers

### 2. Project Prioritization Engine

**Current Challenge:**  
Determining which projects need attention involves complex heuristics across issues, commits, dependencies, and business value.

**MCP Solution:**  
Create `portfolio-priority-server` with tools:
- `get_priorities(filters)` - Ranked list of projects by importance
- `explain_priority(repo_name)` - Breakdown of why a project ranks high/low
- `reorder_priorities(criteria)` - Dynamic re-ranking based on new criteria
- `suggest_next_action(repo_name)` - Recommended next steps for a project

**Value:**  
- "What should I work on next?" becomes answerable by AI
- Transparent prioritization logic accessible to all agents
- Business rules (Echo Vault always high priority for security) encoded and queryable

### 3. Cross-Repository Dependency Analysis

**Current Challenge:**  
Understanding how projects depend on each other (imports, shared libraries, common patterns) requires manual code analysis.

**MCP Solution:**  
Create `portfolio-dependency-server` exposing:
- `build_dependency_graph(include_external)` - Full dependency map
- `find_dependents(repo_name)` - Who depends on this project?
- `find_dependencies(repo_name)` - What does this project depend on?
- `identify_circular_deps()` - Detect circular dependency problems

**Value:**  
- "If I change Echo Vault's API, what breaks?" instant answers
- Impact analysis for breaking changes
- Architectural insights (which projects are too coupled)

### 4. Automated Recommendations & Intelligence

**Current Challenge:**  
Identifying technical debt, security issues, best practice violations across 15 repos is time-consuming.

**MCP Solution:**  
Create `portfolio-recommendations-server` with:
- `generate_recommendations(repo)` - Actionable improvement suggestions
- `audit_security(scope)` - Security assessment across portfolio
- `check_best_practices(repo)` - Compliance with your repo template standards
- `suggest_consolidation()` - Identify duplicate efforts or merge candidates

**Value:**  
- Continuous automated code review across all projects
- Proactive security posture management
- Enforcement of organizational standards

---

## Architecture Integration

### Portfolio Management as Intelligence Layer

```
┌──────────────────────────────────────────────────────────────────────┐
│  Portfolio Management System (GitHub Repo)                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  MCP Server Layer (Python)                                     │  │
│  │  ┌─────────────────┐ ┌──────────────────────┐ ┌───────────────┐      │  │
│  │  │Scanner Server  │ │Priority Server    │ │Dependency    │      │  │
│  │  │                 │ │                    │ │Server        │      │  │
│  │  └─────────────────┘ └──────────────────────┘ └───────────────┘      │  │
│  │  ┌─────────────────────────────────────────────────────────┐      │  │
│  │  │Recommendations Server                                    │      │  │
│  │  └─────────────────────────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Analysis Engine (Scanning, Parsing, Metrics)                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Data Store (Scan Results, Metrics History, Cache)            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
         ↓ MCP Protocol
┌──────────────────────────────────────────────────────────────────────┐
│  MCP Clients (Consumers of Portfolio Intelligence)              │
│  ┌──────────────────┐ ┌────────────────┐ ┌──────────────────┐  │
│  │Control Tower      │ │HeliOS           │ │Claude Desktop    │  │
│  │(Coordination)     │ │Orchestrator     │ │                  │  │
│  └──────────────────┘ └────────────────┘ └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │Custom AI Agents / Scripts                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**Key Pattern:**  
Portfolio Management is a **passive intelligence layer** - it doesn't initiate actions, but provides data for decision-making.

---

## Implementation Roadmap

### Phase 1: Scanner MCP Server (Weeks 1-2)
**Goal:** Expose existing scanning logic via MCP

**Tasks:**
1. Install MCP Python SDK:
   ```bash
   pip install mcp PyGithub gitpython
   ```

2. Create `portfolio-scanner-server`:
   - Tool: `scan_portfolio()` - Trigger full scan
   - Tool: `scan_repo(name)` - Scan specific repository
   - Tool: `get_scan_results(scan_id)` - Retrieve cached results

3. Wrap existing scanning scripts as callable functions
4. Implement result caching (avoid re-scanning on every query)
5. Test with MCP Inspector

**Success Criteria:**
- Can trigger portfolio scan via MCP
- Results returned in structured JSON format
- Cache hit rate >80% for repeated queries

### Phase 2: Priority & Dependency Servers (Weeks 3-5)
**Goal:** Expose prioritization and dependency analysis

**Tasks:**
1. Build `portfolio-priority-server`:
   - Implement scoring algorithm (configurable weights)
   - Tool: `get_priorities(filters)`
   - Tool: `explain_priority(repo)` - Show scoring breakdown
   - Configuration for custom priority rules

2. Build `portfolio-dependency-server`:
   - Parse `import` statements across Python projects
   - Detect shared modules and cross-references
   - Tool: `build_dependency_graph()`
   - Tool: `find_circular_deps()`

3. Create visualization support (JSON output for graph rendering)
4. Integration tests with real portfolio data

**Success Criteria:**
- Priority rankings match manual assessment
- Dependency graph correctly identifies known dependencies
- "What should I work on?" produces actionable answer

### Phase 3: Recommendations Engine (Weeks 6-8)
**Goal:** AI-powered code quality and security suggestions

**Tasks:**
1. Build `portfolio-recommendations-server`:
   - Security audit (outdated dependencies, exposed secrets)
   - Best practices check (using best-practice-repo-template as baseline)
   - Tool: `generate_recommendations(repo)`
   - Tool: `audit_security(scope)`

2. Integrate with external tools:
   - `bandit` for Python security scanning
   - `safety` for dependency vulnerabilities
   - Custom rules for your coding standards

3. Natural language explanation of findings
4. Prioritization of recommendations (critical/high/medium/low)

**Success Criteria:**
- Identifies known security issues in test repos
- Recommendations are actionable (not generic)
- False positive rate <10%

### Phase 4: Control Tower Integration (Weeks 9-10)
**Goal:** Portfolio Management as data source for Control Tower

**Tasks:**
1. Register Portfolio Management servers with Control Tower
2. Implement authentication/authorization between systems
3. Create unified query interface:
   - Control Tower delegates portfolio queries to Portfolio Management
   - Results aggregated with other Control Tower data

4. Build monitoring for cross-system communication
5. Performance optimization (parallel queries, caching)

**Success Criteria:**
- Control Tower can query portfolio health via MCP
- Response time for combined queries <3 seconds
- No authentication failures in production

### Phase 5: Advanced Analytics (Weeks 11-12)
**Goal:** Trend analysis and predictive insights

**Tasks:**
1. Historical data collection (track metrics over time)
2. Trend analysis:
   - Project velocity trends
   - Issue accumulation rates
   - Commit frequency patterns

3. Predictive models:
   - Project completion estimation
   - Risk scoring (likelihood of project stalling)
   - Anomaly detection (unusual activity spikes)

4. Weekly/monthly automated reports
5. Dashboard integration (optional)

**Success Criteria:**
- 6 months of historical data collected
- Completion predictions within ±30% actual
- Anomaly detection catches manually-observed issues

---

## Technical Implementation

### Scanner Server Example

```python
# mcp_servers/scanner_server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from github import Github
import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

server = Server("portfolio-scanner")
gh = Github(os.getenv("GITHUB_TOKEN"))

# Cache directory
CACHE_DIR = Path("/tmp/portfolio_cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL = timedelta(hours=6)

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="scan_portfolio",
            description="Scan entire GitHub portfolio for health, activity, and metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_private": {
                        "type": "boolean",
                        "description": "Include private repositories",
                        "default": True
                    },
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Bypass cache and force fresh scan",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="scan_repo",
            description="Deep scan of a specific repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Repository name (e.g., 'project-echo-vault-local')"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["basic", "detailed", "comprehensive"],
                        "default": "detailed"
                    }
                },
                "required": ["repo_name"]
            }
        ),
        Tool(
            name="compare_repos",
            description="Side-by-side comparison of multiple repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of repository names to compare"
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["activity", "health", "issues", "size"]
                    }
                },
                "required": ["repo_names"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "scan_portfolio":
        include_private = arguments.get("include_private", True)
        force_refresh = arguments.get("force_refresh", False)
        
        cache_key = f"portfolio_scan_{include_private}"
        cached_result = get_cached_result(cache_key) if not force_refresh else None
        
        if cached_result:
            return [TextContent(type="text", text=json.dumps({
                "cached": True,
                "scan_time": cached_result["scan_time"],
                "results": cached_result["results"]
            }, indent=2))]
        
        # Perform actual scan
        repos = list(gh.get_user().get_repos())
        if not include_private:
            repos = [r for r in repos if not r.private]
        
        results = []
        for repo in repos:
            scan_result = scan_repository_basic(repo)
            results.append(scan_result)
        
        # Cache results
        scan_data = {
            "scan_time": datetime.now().isoformat(),
            "results": results
        }
        cache_result(cache_key, scan_data)
        
        return [TextContent(type="text", text=json.dumps({
            "cached": False,
            "scan_time": scan_data["scan_time"],
            "results": results
        }, indent=2))]
    
    elif name == "scan_repo":
        repo_name = arguments["repo_name"]
        depth = arguments.get("depth", "detailed")
        
        full_name = f"zebadee2kk/{repo_name}" if "/" not in repo_name else repo_name
        repo = gh.get_repo(full_name)
        
        if depth == "basic":
            result = scan_repository_basic(repo)
        elif depth == "comprehensive":
            result = scan_repository_comprehensive(repo)
        else:  # detailed
            result = scan_repository_detailed(repo)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "compare_repos":
        repo_names = arguments["repo_names"]
        criteria = arguments.get("criteria", ["activity", "health", "issues", "size"])
        
        comparison = []
        for repo_name in repo_names:
            full_name = f"zebadee2kk/{repo_name}" if "/" not in repo_name else repo_name
            try:
                repo = gh.get_repo(full_name)
                repo_data = {
                    "name": repo_name,
                    "comparison_data": {}
                }
                
                if "activity" in criteria:
                    commits = list(repo.get_commits()[:10])
                    repo_data["comparison_data"]["recent_commits"] = len(commits)
                    repo_data["comparison_data"]["last_commit_date"] = commits[0].commit.author.date.isoformat() if commits else None
                
                if "health" in criteria:
                    repo_data["comparison_data"]["health_score"] = calculate_health_score(repo)
                
                if "issues" in criteria:
                    repo_data["comparison_data"]["open_issues"] = repo.open_issues_count
                
                if "size" in criteria:
                    repo_data["comparison_data"]["size_kb"] = repo.size
                
                comparison.append(repo_data)
            except Exception as e:
                comparison.append({"name": repo_name, "error": str(e)})
        
        return [TextContent(type="text", text=json.dumps(comparison, indent=2))]
    
    raise ValueError(f"Unknown tool: {name}")

def scan_repository_basic(repo):
    return {
        "name": repo.full_name,
        "description": repo.description,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "language": repo.language,
        "private": repo.private,
        "last_updated": repo.updated_at.isoformat()
    }

def scan_repository_detailed(repo):
    basic = scan_repository_basic(repo)
    
    # Add commit activity
    commits = list(repo.get_commits()[:10])
    basic["recent_commit_count"] = len(commits)
    basic["last_commit_date"] = commits[0].commit.author.date.isoformat() if commits else None
    
    # Health score
    basic["health_score"] = calculate_health_score(repo)
    
    # License
    basic["license"] = repo.license.name if repo.license else None
    
    return basic

def scan_repository_comprehensive(repo):
    detailed = scan_repository_detailed(repo)
    
    # Add contributors
    contributors = list(repo.get_contributors())
    detailed["contributor_count"] = len(contributors)
    
    # Add topics/tags
    detailed["topics"] = repo.get_topics()
    
    # Add file structure analysis
    try:
        contents = repo.get_contents("")
        root_files = [c.name for c in contents if c.type == "file"]
        detailed["root_files"] = root_files
        detailed["has_readme"] = "README.md" in root_files
        detailed["has_license"] = "LICENSE" in root_files
    except:
        pass
    
    return detailed

def calculate_health_score(repo) -> float:
    """Calculate 0-100 health score"""
    score = 100.0
    
    # Penalty for open issues
    score -= min(repo.open_issues_count * 2, 40)
    
    # Penalty for staleness
    days_since_update = (datetime.now(datetime.timezone.utc) - repo.updated_at).days
    if days_since_update > 30:
        score -= min((days_since_update - 30) * 0.5, 30)
    
    # Bonus for recent activity
    if days_since_update < 7:
        score += 10
    
    return max(0, min(100, score))

def get_cached_result(cache_key):
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mtime < CACHE_TTL:
            with open(cache_file) as f:
                return json.load(f)
    return None

def cache_result(cache_key, data):
    cache_file = CACHE_DIR / f"{cache_key}.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    mcp.server.stdio.stdio_server(server)
```

---

## Integration Patterns

### With Control Tower

Control Tower queries Portfolio Management for project health:

```python
# Control Tower coordinator server
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_portfolio_health":
        # Delegate to Portfolio Management MCP server
        portfolio_client = create_mcp_client("portfolio-scanner")
        scan_results = await portfolio_client.call_tool("scan_portfolio", {})
        
        # Aggregate and enrich with Control Tower data
        enriched_results = enrich_with_dependencies(scan_results)
        return enriched_results
```

### With HeliOS

HeliOS uses Portfolio Management for task prioritization:

```python
# HeliOS asks: "What project needs my attention?"
# 1. Query Portfolio Management for priorities
priority_results = await portfolio_priority_client.call_tool(
    "get_priorities",
    {"filters": {"tags": ["security"], "min_health": 60}}
)

# 2. Route to appropriate project-specific AI agent
top_project = priority_results[0]
if top_project["name"] == "project-echo-vault-local":
    delegate_to_echo_vault_agent(top_project)
```

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Stale cache returns outdated data | Medium | Medium | - TTL enforcement<br>- Cache invalidation on repo updates<br>- "force_refresh" option |
| Scanning rate limits (GitHub API) | High | High | - Aggressive caching<br>- Incremental scans<br>- Token rotation |
| Privacy: Exposing private repo data | Low | Critical | - Authentication required<br>- Access control per repo<br>- Audit logging |
| Performance degradation with large portfolios | Medium | Medium | - Parallel scanning<br>- Background jobs<br>- Pagination |
| Dependency analysis false positives | Medium | Low | - Manual review workflow<br>- Confidence scoring<br>- User feedback loop |

---

## Monitoring & Success Metrics

### Key Metrics

1. **Scanning Performance**
   - Average scan time (full portfolio)
   - Cache hit rate
   - GitHub API quota utilization

2. **Usage Patterns**
   - Most queried tools
   - Peak usage times
   - Client distribution (Control Tower vs HeliOS vs manual)

3. **Data Quality**
   - Health score correlation with manual assessment
   - Recommendation acceptance rate
   - False positive rate for security findings

### Dashboards

- Portfolio overview (health scores, trends)
- Scanning activity (requests/day, cache performance)
- Recommendation pipeline (generated, accepted, resolved)

---

## Next Steps for Project Manager

### Immediate Actions (This Week)

1. **Review & Approve Plan**
   - Validate portfolio-as-intelligence-layer pattern
   - Approve 12-week roadmap
   - Identify resource requirements

2. **Environment Setup**
   - Ensure GitHub token has appropriate scopes
   - Setup cache directory (/tmp or persistent storage)
   - Install MCP Python SDK

3. **Create Project Tracking**
   - GitHub issues for each phase
   - Milestones aligned with Control Tower and Echo Vault

### Decision Points

- [ ] Approve MCP as exposure layer for portfolio analytics?
- [ ] Commit to 12-week implementation timeline?
- [ ] Define caching strategy (TTL, storage location)?
- [ ] Integrate with Control Tower in Phase 4?

### Resources Needed

- Python developer (GitHub API, data analysis) - 0.75 FTE
- Integration with Control Tower - coordination with Control Tower team
- GitHub token (fine-grained, read access to all repos)
- Optional: Database for historical metrics (SQLite sufficient)

---

## References

1. **MCP Official Resources**
   - Python SDK: https://github.com/modelcontextprotocol/python-sdk
   - Documentation: https://modelcontextprotocol.io

2. **Related Portfolio Management Documents**
   - Architecture: `docs/ARCHITECTURE.md` (TBD)
   - Scanning Strategy: `docs/SCANNING.md` (TBD)

3. **Cross-Project Integration**
   - Control Tower MCP Plan: `../control-tower/docs/research/MCP_INTEGRATION_PLAN.md` ✓
   - Echo Vault MCP Plan: `../project-echo-vault-local/docs/research/MCP_INTEGRATION_PLAN.md` ✓

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-25  
**Next Review:** Upon Phase 1 completion or 2026-03-11

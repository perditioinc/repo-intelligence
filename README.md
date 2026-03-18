# repo-intelligence

> Score any GitHub repo 0–100 across README quality, activity, community health, and CI/CD. Pip-installable.

## Install

```bash
pip install git+https://github.com/perditioinc/repo-intelligence.git
```

## Quick Start

```bash
export GH_TOKEN=your_token
repo-score langchain-ai/langchain
```

Output:
```
langchain-ai/langchain: 87/100 (Grade: B)
  README:    22/25  ✓ readme_exists ✓ readme_500_chars ✓ readme_2000_chars ✓ readme_code_blocks ✗ readme_badges
  Activity:  25/25  ✓ committed_30d ✓ commits_gt_10 ✓ has_releases
  Community: 20/25  ✓ has_license ✓ issues_enabled ✓ has_changelog_or_releases ✗ has_contributing
  CI:        20/25  ✓ has_workflows ✓ has_tests_dir ✗ has_build_config
```

## Scoring Table

| Category | Check | Points |
|----------|-------|--------|
| README | exists | 5 |
| README | >500 chars | 5 |
| README | >2000 chars | 5 |
| README | has ``` blocks | 5 |
| README | has badges | 5 |
| Activity | committed last 30d | 10 |
| Activity | committed last 90d (else) | 7 |
| Activity | committed last 365d (else) | 3 |
| Activity | >10 commits | 5 |
| Activity | has releases | 5 |
| Community | has LICENSE | 10 |
| Community | has CONTRIBUTING.md | 5 |
| Community | issues enabled | 5 |
| Community | CHANGELOG or releases | 5 |
| CI | has .github/workflows/ | 10 |
| CI | has tests/ or test/ | 10 |
| CI | has pyproject.toml or package.json | 5 |

**Grades:** A=90+, B=75+, C=60+, D=40+, F<40

## Python API

```python
import asyncio
from repo_intelligence import score_repo, score_repos_batch

# Single repo
score = asyncio.run(score_repo("tiangolo", "fastapi", token="ghp_..."))
print(f"{score.total}/100 Grade: {score.grade}")
print(score.to_dict())

# Batch (concurrent)
repos = [("tiangolo", "fastapi"), ("pydantic", "pydantic")]
scores = asyncio.run(score_repos_batch(repos, token="ghp_...", concurrency=5))
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GH_TOKEN | yes | — | GitHub PAT (read:repo scope) |
| CONCURRENCY_CHECKS | no | 10 | Parallel checks per batch |

## How reporium-db Uses This

reporium-db calls `score_repos_batch` nightly to score newly added or updated repos.
Scores are stored alongside metadata and surfaced in the reporium.com UI for filtering and ranking.

## Contributing

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
```

## License

MIT

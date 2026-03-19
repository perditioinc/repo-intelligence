# repo-intelligence

> Score any GitHub repo 0-100 across README quality, activity, community health, and CI/CD. Pip-installable.

## Install

```bash
pip install git+https://github.com/perditioinc/repo-intelligence.git
```

## Quick Start

```bash
export GH_TOKEN=your_token
repo-score tiangolo/fastapi
```

Output:
```
tiangolo/fastapi: 95/100 (Grade: A)
  README:    25/25  check readme_exists check readme_500_chars check readme_2000_chars check readme_code_blocks check readme_badges
  Activity:  20/25  check committed_30d check commits_gt_10 check has_releases
  Community: 25/25  check has_license check has_contributing check issues_enabled check has_changelog_or_releases
  CI:        25/25  check has_workflows check has_tests_dir check has_build_config
```

## Scoring Rubric

| Category | Check | Points | Max |
|----------|-------|--------|-----|
| README | exists | 5 | |
| README | >500 chars | 5 | |
| README | >2000 chars | 5 | |
| README | has ``` blocks | 5 | |
| README | has badges | 5 | **25** |
| Activity | committed last 30d | 10 | |
| Activity | committed last 90d (if not 30d) | 7 | |
| Activity | committed last 365d (if not 90d) | 3 | |
| Activity | >10 commits | 5 | |
| Activity | has releases | 5 | **25** |
| Community | has LICENSE | 10 | |
| Community | has CONTRIBUTING.md | 5 | |
| Community | issues enabled | 5 | |
| Community | CHANGELOG or releases | 5 | **25** |
| CI | has .github/workflows/ | 10 | |
| CI | has tests/ or test/ | 10 | |
| CI | has pyproject.toml or package.json | 5 | **25** |

**Grades:** A=90+, B=75+, C=60+, D=40+, F<40

**Note:** Activity recency checks are mutually exclusive tiers (30d > 90d > 365d).

## Python API

```python
import asyncio
from repo_intelligence import score_repo, score_repos_batch

# Single repo
score = asyncio.run(score_repo("tiangolo", "fastapi", token="ghp_..."))
print(f"{score.total}/100  Grade: {score.grade}")
print(score.to_dict())

# Batch (concurrent)
repos = [("tiangolo", "fastapi"), ("pydantic", "pydantic"), ("huggingface", "transformers")]
scores = asyncio.run(score_repos_batch(repos, token="ghp_...", concurrency=5))
for s in scores:
    print(f"{s.owner}/{s.repo}: {s.total}/100 ({s.grade})")
```

Batch output:
```
tiangolo/fastapi: 95/100 (A)
pydantic/pydantic: 90/100 (A)
huggingface/transformers: 90/100 (A)
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GH_TOKEN | yes | - | GitHub PAT (read:repo scope) |
| CONCURRENCY_CHECKS | no | 10 | Parallel checks per batch |

## How reporium-db Uses This

reporium-db calls `score_repos_batch` nightly to score newly added or updated repos.
Scores are stored alongside metadata and surfaced in the reporium.com UI for filtering and ranking.

Each repo in `pending_enrichment.json` is scored on its next run. Scores feed into the
reporium-api search index, enabling users to filter by quality grade.

## Contributing

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
```

## License

MIT

"""CI/CD quality checks (25 pts total)."""

from __future__ import annotations

import logging
from typing import Optional

from ..client import GitHubClient
from ..models import CheckResult

logger = logging.getLogger(__name__)


async def check_ci(client: GitHubClient, owner: str, repo: str) -> list[CheckResult]:
    """Run all CI/CD checks for a repository.

    Checks:
    - has .github/workflows/ (10 pts)
    - has tests/ or test/ directory (10 pts)
    - has pyproject.toml or package.json (5 pts)

    Args:
        client: Authenticated GitHub client.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        List of CheckResult for each CI check.
    """
    workflows: Optional[list] = await client.get(
        f"/repos/{owner}/{repo}/contents/.github/workflows"
    )
    tests_dir: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/contents/tests")
    test_dir: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/contents/test")
    pyproject: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/contents/pyproject.toml")
    package_json: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/contents/package.json")

    has_workflows = workflows is not None and (isinstance(workflows, list) and len(workflows) > 0)
    has_tests = tests_dir is not None or test_dir is not None
    has_build_config = pyproject is not None or package_json is not None

    return [
        CheckResult(
            "has_workflows",
            10,
            has_workflows,
            "GitHub Actions workflows present" if has_workflows else "No .github/workflows/",
        ),
        CheckResult(
            "has_tests_dir",
            10,
            has_tests,
            "tests/ or test/ directory present" if has_tests else "No tests directory",
        ),
        CheckResult(
            "has_build_config",
            5,
            has_build_config,
            "pyproject.toml or package.json present" if has_build_config else "No build config",
        ),
    ]

"""Community health checks (25 pts total)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..client import GitHubClient
from ..models import CheckResult

logger = logging.getLogger(__name__)


async def check_community(client: GitHubClient, owner: str, repo: str) -> list[CheckResult]:
    """Run all community health checks for a repository.

    Checks:
    - has LICENSE (10 pts)
    - has CONTRIBUTING.md (5 pts)
    - issues enabled (5 pts)
    - CHANGELOG or releases (5 pts)

    Args:
        client: Authenticated GitHub client.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        List of CheckResult for each community check.
    """
    repo_data: Optional[dict[str, Any]] = await client.get(f"/repos/{owner}/{repo}")
    license_data: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/license")
    contributing: Optional[dict] = await client.get(
        f"/repos/{owner}/{repo}/contents/CONTRIBUTING.md"
    )
    changelog: Optional[dict] = await client.get(f"/repos/{owner}/{repo}/contents/CHANGELOG.md")
    releases: Optional[list] = await client.get(f"/repos/{owner}/{repo}/releases?per_page=1")

    has_license = license_data is not None
    has_contributing = contributing is not None
    issues_enabled = bool(repo_data and repo_data.get("has_issues", False))
    has_changelog_or_releases = changelog is not None or bool(releases)

    return [
        CheckResult(
            "has_license",
            10,
            has_license,
            "License present" if has_license else "No license",
        ),
        CheckResult(
            "has_contributing",
            5,
            has_contributing,
            "CONTRIBUTING.md present" if has_contributing else "No CONTRIBUTING.md",
        ),
        CheckResult(
            "issues_enabled",
            5,
            issues_enabled,
            "Issues enabled" if issues_enabled else "Issues disabled",
        ),
        CheckResult(
            "has_changelog_or_releases",
            5,
            has_changelog_or_releases,
            "CHANGELOG or releases present" if has_changelog_or_releases else "No changelog",
        ),
    ]

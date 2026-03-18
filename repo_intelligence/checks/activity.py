"""Activity checks (25 pts total)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..client import GitHubClient
from ..models import CheckResult

logger = logging.getLogger(__name__)


def _days_since(iso: Optional[str]) -> Optional[int]:
    """Return days since an ISO-8601 timestamp.

    Args:
        iso: ISO-8601 timestamp string or None.

    Returns:
        Number of days since the timestamp, or None if unparseable.
    """
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except ValueError:
        return None


async def check_activity(client: GitHubClient, owner: str, repo: str) -> list[CheckResult]:
    """Run all activity checks for a repository.

    Checks (mutually exclusive for recency):
    - committed last 30d (10 pts)
    - committed last 90d — else (7 pts)
    - committed last 365d — else (3 pts)
    - >10 commits (5 pts)
    - has releases (5 pts)

    Args:
        client: Authenticated GitHub client.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        List of CheckResult for each activity check.
    """
    repo_data: Optional[dict[str, Any]] = await client.get(f"/repos/{owner}/{repo}")
    commits_data: Optional[list] = await client.get(f"/repos/{owner}/{repo}/commits?per_page=11")
    releases_data: Optional[list] = await client.get(f"/repos/{owner}/{repo}/releases?per_page=1")

    pushed_at = repo_data.get("pushed_at") if repo_data else None
    days = _days_since(pushed_at)
    commit_count = len(commits_data) if isinstance(commits_data, list) else 0
    has_releases = bool(releases_data)

    # Recency: mutually exclusive tiers
    committed_30d = days is not None and days <= 30
    committed_90d = (not committed_30d) and (days is not None and days <= 90)
    committed_365d = (
        (not committed_30d) and (not committed_90d) and (days is not None and days <= 365)
    )

    return [
        CheckResult(
            "committed_30d",
            10,
            committed_30d,
            f"{days}d ago" if days is not None else "unknown",
        ),
        CheckResult(
            "committed_90d",
            7,
            committed_90d,
            f"{days}d ago" if days is not None else "unknown",
        ),
        CheckResult(
            "committed_365d",
            3,
            committed_365d,
            f"{days}d ago" if days is not None else "unknown",
        ),
        CheckResult(
            "commits_gt_10",
            5,
            commit_count > 10,
            f"{commit_count}+ commits" if commit_count == 11 else f"{commit_count} commits",
        ),
        CheckResult(
            "has_releases",
            5,
            has_releases,
            "Has releases" if has_releases else "No releases",
        ),
    ]

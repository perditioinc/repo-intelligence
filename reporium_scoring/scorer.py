"""Orchestrate all checks and produce a RepoScore."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

from .checks.activity import check_activity
from .checks.ci import check_ci
from .checks.community import check_community
from .checks.readme import check_readme
from .client import GitHubClient
from .models import RepoScore

logger = logging.getLogger(__name__)

GRADE_THRESHOLDS = [(90, "A"), (75, "B"), (60, "C"), (40, "D")]


def _grade(total: int) -> str:
    """Return the letter grade for a total score.

    Args:
        total: Score out of 100.

    Returns:
        Letter grade: A, B, C, D, or F.
    """
    for threshold, grade in GRADE_THRESHOLDS:
        if total >= threshold:
            return grade
    return "F"


async def score_repo(
    owner: str,
    repo: str,
    token: str,
    http: Optional[httpx.AsyncClient] = None,
) -> RepoScore:
    """Score a single GitHub repository across all four check categories.

    Args:
        owner: Repository owner (user or org).
        repo: Repository name.
        token: GitHub personal access token.
        http: Optional shared httpx.AsyncClient for testing.

    Returns:
        RepoScore with total, grade, and per-category check results.
    """
    try:
        async with GitHubClient(token, http) as client:
            readme_checks, activity_checks, community_checks, ci_checks = await asyncio.gather(
                check_readme(client, owner, repo),
                check_activity(client, owner, repo),
                check_community(client, owner, repo),
                check_ci(client, owner, repo),
            )

        total = sum(
            c.points
            for checks in (readme_checks, activity_checks, community_checks, ci_checks)
            for c in checks
            if c.passed
        )

        return RepoScore(
            owner=owner,
            repo=repo,
            total=total,
            grade=_grade(total),
            readme_checks=readme_checks,
            activity_checks=activity_checks,
            community_checks=community_checks,
            ci_checks=ci_checks,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error scoring %s/%s: %s", owner, repo, exc, exc_info=True)
        return RepoScore(
            owner=owner,
            repo=repo,
            total=0,
            grade="F",
            error=str(exc),
        )


async def score_repos_batch(
    repos: list[tuple[str, str]],
    token: str,
    concurrency: int = 10,
) -> list[RepoScore]:
    """Score multiple repositories concurrently.

    Args:
        repos: List of (owner, repo) tuples.
        token: GitHub personal access token.
        concurrency: Maximum parallel requests.

    Returns:
        List of RepoScore in the same order as input.
    """
    sem = asyncio.Semaphore(concurrency)

    async def _with_sem(owner: str, repo: str) -> RepoScore:
        """Score one repo under the semaphore."""
        async with sem:
            return await score_repo(owner, repo, token)

    return list(await asyncio.gather(*[_with_sem(o, r) for o, r in repos]))

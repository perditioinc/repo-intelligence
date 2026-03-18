"""Example usage of repo-intelligence with real public repos."""

from __future__ import annotations

import asyncio
import os

from repo_intelligence import score_repo, score_repos_batch


async def single_repo_example() -> None:
    """Score a single public repository."""
    token = os.environ["GH_TOKEN"]
    score = await score_repo("tiangolo", "fastapi", token)
    print(f"{score.owner}/{score.repo}: {score.total}/100 (Grade: {score.grade})")
    print(f"  README: {score.readme_score}/25")
    print(f"  Activity: {score.activity_score}/25")
    print(f"  Community: {score.community_score}/25")
    print(f"  CI: {score.ci_score}/25")


async def batch_example() -> None:
    """Score multiple public repositories concurrently."""
    token = os.environ["GH_TOKEN"]
    repos = [
        ("tiangolo", "fastapi"),
        ("pydantic", "pydantic"),
        ("huggingface", "transformers"),
    ]
    scores = await score_repos_batch(repos, token, concurrency=3)
    for s in sorted(scores, key=lambda x: -x.total):
        print(f"{s.owner}/{s.repo}: {s.total}/100 (Grade: {s.grade})")


if __name__ == "__main__":
    asyncio.run(batch_example())

"""CLI: repo-score owner/repo."""

from __future__ import annotations

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def _tick(passed: bool) -> str:
    """Return ✓ or ✗ symbol."""
    return "✓" if passed else "✗"


def _format_checks(checks: list) -> str:
    """Format a list of CheckResult as a compact symbol line.

    Args:
        checks: List of CheckResult objects.

    Returns:
        Space-separated check symbols and names.
    """
    return " ".join(f"{_tick(c.passed)} {c.name}" for c in checks)


def _print_score(score) -> None:
    """Print a formatted RepoScore to stdout.

    Args:
        score: RepoScore object to display.
    """
    if score.error:
        print(f"{score.owner}/{score.repo}: ERROR — {score.error}")
        return

    print(f"{score.owner}/{score.repo}: {score.total}/100 (Grade: {score.grade})")
    print(f"  README:    {score.readme_score:2d}/25  {_format_checks(score.readme_checks)}")
    print(f"  Activity:  {score.activity_score:2d}/25  {_format_checks(score.activity_checks)}")
    print(f"  Community: {score.community_score:2d}/25  {_format_checks(score.community_checks)}")
    print(f"  CI:        {score.ci_score:2d}/25  {_format_checks(score.ci_checks)}")


def main() -> None:
    """Entry point for the repo-score CLI command."""
    from .config import load_config
    from .scorer import score_repo

    if len(sys.argv) < 2:
        print("Usage: repo-score owner/repo [owner/repo ...]")
        sys.exit(1)

    config = load_config()

    async def _run() -> None:
        """Score all provided repos and print results."""
        for arg in sys.argv[1:]:
            if "/" not in arg:
                print(f"Invalid format: {arg!r} — expected 'owner/repo'")
                continue
            owner, repo = arg.split("/", 1)
            score = await score_repo(owner, repo, config.gh_token)
            _print_score(score)

    asyncio.run(_run())

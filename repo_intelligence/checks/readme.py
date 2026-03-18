"""README quality checks (25 pts total)."""

from __future__ import annotations

import base64
import logging
from typing import Any, Optional

from ..client import GitHubClient
from ..models import CheckResult

logger = logging.getLogger(__name__)

MAX_POINTS = 25


async def check_readme(client: GitHubClient, owner: str, repo: str) -> list[CheckResult]:
    """Run all README checks for a repository.

    Checks:
    - exists (5 pts)
    - >500 chars (5 pts)
    - >2000 chars (5 pts)
    - has code blocks (5 pts)
    - has badges (5 pts)

    Args:
        client: Authenticated GitHub client.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        List of CheckResult for each readme check.
    """
    data: Optional[dict[str, Any]] = await client.get(f"/repos/{owner}/{repo}/readme")

    exists = data is not None
    content = ""
    if exists and data:
        try:
            content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not decode README for %s/%s: %s", owner, repo, exc)

    length = len(content)

    return [
        CheckResult("readme_exists", 5, exists, "README file present" if exists else "No README"),
        CheckResult(
            "readme_500_chars",
            5,
            length > 500,
            f"{length} chars" if exists else "N/A",
        ),
        CheckResult(
            "readme_2000_chars",
            5,
            length > 2000,
            f"{length} chars" if exists else "N/A",
        ),
        CheckResult(
            "readme_code_blocks",
            5,
            "```" in content,
            "Has code blocks" if "```" in content else "No code blocks",
        ),
        CheckResult(
            "readme_badges",
            5,
            "![" in content or "[![" in content,
            "Has badges" if ("![" in content or "[![" in content) else "No badges",
        ),
    ]

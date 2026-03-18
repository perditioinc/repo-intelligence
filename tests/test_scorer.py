"""Tests for repo_intelligence.scorer."""

from __future__ import annotations

import base64

import httpx
import respx

from repo_intelligence.client import GITHUB_API
from repo_intelligence.scorer import _grade, score_repo, score_repos_batch

OWNER = "test-owner"
REPO = "test-repo"


def _readme(text: str) -> dict:
    """Build a GitHub /readme JSON response."""
    return {"content": base64.b64encode(text.encode()).decode() + "\n", "encoding": "base64"}


def _mock_all_404(owner: str = OWNER, repo: str = REPO) -> None:
    """Register 404 mocks for all check endpoints."""
    endpoints = [
        f"/repos/{owner}/{repo}/readme",
        f"/repos/{owner}/{repo}/license",
        f"/repos/{owner}/{repo}/contents/CONTRIBUTING.md",
        f"/repos/{owner}/{repo}/contents/CHANGELOG.md",
        f"/repos/{owner}/{repo}/contents/.github/workflows",
        f"/repos/{owner}/{repo}/contents/tests",
        f"/repos/{owner}/{repo}/contents/test",
        f"/repos/{owner}/{repo}/contents/pyproject.toml",
        f"/repos/{owner}/{repo}/contents/package.json",
    ]
    for ep in endpoints:
        respx.get(f"{GITHUB_API}{ep}").mock(return_value=httpx.Response(404))

    respx.get(f"{GITHUB_API}/repos/{owner}/{repo}").mock(
        return_value=httpx.Response(
            200, json={"pushed_at": "2020-01-01T00:00:00Z", "has_issues": False}
        )
    )
    respx.get(f"{GITHUB_API}/repos/{owner}/{repo}/commits", params={"per_page": "11"}).mock(
        return_value=httpx.Response(200, json=[])
    )
    respx.get(f"{GITHUB_API}/repos/{owner}/{repo}/releases", params={"per_page": "1"}).mock(
        return_value=httpx.Response(200, json=[])
    )


# ── _grade ────────────────────────────────────────────────────────────────────


def test_grade_a():
    assert _grade(95) == "A"


def test_grade_b():
    assert _grade(80) == "B"


def test_grade_c():
    assert _grade(65) == "C"


def test_grade_d():
    assert _grade(45) == "D"


def test_grade_f():
    assert _grade(30) == "F"


# ── score_repo ────────────────────────────────────────────────────────────────


@respx.mock
async def test_score_repo_returns_score():
    """score_repo returns a RepoScore with a total and grade."""
    _mock_all_404()
    score = await score_repo(OWNER, REPO, "test-token")
    assert score.total >= 0
    assert score.grade in ("A", "B", "C", "D", "F")
    assert score.owner == OWNER
    assert score.repo == REPO


@respx.mock
async def test_score_repo_low_score():
    """All-404 endpoints produce a low total score."""
    _mock_all_404()
    score = await score_repo(OWNER, REPO, "test-token")
    assert score.total < 25  # no readme, no license, no recent activity


@respx.mock
async def test_score_repo_has_all_check_categories():
    """Returned score has all four check category lists."""
    _mock_all_404()
    score = await score_repo(OWNER, REPO, "test-token")
    assert isinstance(score.readme_checks, list)
    assert isinstance(score.activity_checks, list)
    assert isinstance(score.community_checks, list)
    assert isinstance(score.ci_checks, list)


@respx.mock
async def test_score_repo_handles_network_error():
    """Returns a score with error field on unexpected failure."""
    respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/readme").mock(
        side_effect=httpx.ConnectError("timeout")
    )
    # Other endpoints return 404
    for ep in [
        f"/repos/{OWNER}/{REPO}/license",
        f"/repos/{OWNER}/{REPO}/contents/CONTRIBUTING.md",
        f"/repos/{OWNER}/{REPO}/contents/CHANGELOG.md",
        f"/repos/{OWNER}/{REPO}/contents/.github/workflows",
        f"/repos/{OWNER}/{REPO}/contents/tests",
        f"/repos/{OWNER}/{REPO}/contents/test",
        f"/repos/{OWNER}/{REPO}/contents/pyproject.toml",
        f"/repos/{OWNER}/{REPO}/contents/package.json",
    ]:
        respx.get(f"{GITHUB_API}{ep}").mock(return_value=httpx.Response(404))
    respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}").mock(
        return_value=httpx.Response(
            200, json={"pushed_at": "2020-01-01T00:00:00Z", "has_issues": False}
        )
    )
    respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/commits", params={"per_page": "11"}).mock(
        return_value=httpx.Response(200, json=[])
    )
    respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/releases", params={"per_page": "1"}).mock(
        return_value=httpx.Response(200, json=[])
    )

    score = await score_repo(OWNER, REPO, "test-token")
    assert score.error is not None
    assert score.total == 0


@respx.mock
async def test_score_repos_batch():
    """score_repos_batch returns one score per input repo."""
    _mock_all_404("owner-a", "repo-a")
    _mock_all_404("owner-b", "repo-b")
    scores = await score_repos_batch(
        [("owner-a", "repo-a"), ("owner-b", "repo-b")], "test-token", concurrency=2
    )
    assert len(scores) == 2


@respx.mock
async def test_score_repo_grades():
    """to_dict() includes grade and all numeric scores."""
    _mock_all_404()
    score = await score_repo(OWNER, REPO, "test-token")
    d = score.to_dict()
    assert "grade" in d
    assert "total" in d
    assert "readme_score" in d

"""Shared fixtures for repo-intelligence tests."""

from __future__ import annotations

import base64

import httpx
import pytest
import respx

from repo_intelligence.client import GITHUB_API

OWNER = "test-owner"
REPO = "test-repo"


def _readme_content(text: str) -> dict:
    """Build a GitHub /readme response for the given text."""
    return {
        "content": base64.b64encode(text.encode()).decode() + "\n",
        "encoding": "base64",
    }


@pytest.fixture
def high_score_mocks():
    """Mock all GitHub endpoints to produce a near-perfect score."""
    long_readme = (
        "# Title\n\n"
        + "A" * 2100
        + "\n```python\nprint('hello')\n```\n"
        + "![badge](https://img.shields.io/badge/test-green)"
    )

    with respx.mock:
        # README — long, code blocks, badges
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/readme").mock(
            return_value=httpx.Response(200, json=_readme_content(long_readme))
        )
        # Repo — pushed recently, issues enabled
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}").mock(
            return_value=httpx.Response(
                200,
                json={
                    "pushed_at": "2026-03-16T10:00:00Z",
                    "has_issues": True,
                    "stargazers_count": 100,
                },
            )
        )
        # Commits — 11+ (>10 threshold)
        respx.get(
            f"{GITHUB_API}/repos/{OWNER}/{REPO}/commits",
            params={"per_page": "11"},
        ).mock(return_value=httpx.Response(200, json=[{}] * 11))
        # Releases — has releases
        respx.get(
            f"{GITHUB_API}/repos/{OWNER}/{REPO}/releases",
            params={"per_page": "1"},
        ).mock(return_value=httpx.Response(200, json=[{"id": 1}]))
        # License
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/license").mock(
            return_value=httpx.Response(200, json={"license": {"key": "mit"}})
        )
        # Contributing
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/CONTRIBUTING.md").mock(
            return_value=httpx.Response(200, json={"name": "CONTRIBUTING.md"})
        )
        # Changelog
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/CHANGELOG.md").mock(
            return_value=httpx.Response(200, json={"name": "CHANGELOG.md"})
        )
        # Workflows
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/.github/workflows").mock(
            return_value=httpx.Response(200, json=[{"name": "test.yml"}])
        )
        # tests/
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/tests").mock(
            return_value=httpx.Response(200, json=[{"name": "test_foo.py"}])
        )
        # test/ — 404
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/test").mock(
            return_value=httpx.Response(404)
        )
        # pyproject.toml
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/pyproject.toml").mock(
            return_value=httpx.Response(200, json={"name": "pyproject.toml"})
        )
        # package.json — 404
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/package.json").mock(
            return_value=httpx.Response(404)
        )
        yield


@pytest.fixture
def low_score_mocks():
    """Mock all GitHub endpoints to produce a near-zero score."""
    with respx.mock:
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/readme").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}").mock(
            return_value=httpx.Response(
                200,
                json={"pushed_at": "2020-01-01T00:00:00Z", "has_issues": False},
            )
        )
        respx.get(
            f"{GITHUB_API}/repos/{OWNER}/{REPO}/commits",
            params={"per_page": "11"},
        ).mock(return_value=httpx.Response(200, json=[{}] * 3))
        respx.get(
            f"{GITHUB_API}/repos/{OWNER}/{REPO}/releases",
            params={"per_page": "1"},
        ).mock(return_value=httpx.Response(200, json=[]))
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/license").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/CONTRIBUTING.md").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/CHANGELOG.md").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/.github/workflows").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/tests").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/test").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/pyproject.toml").mock(
            return_value=httpx.Response(404)
        )
        respx.get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/contents/package.json").mock(
            return_value=httpx.Response(404)
        )
        yield

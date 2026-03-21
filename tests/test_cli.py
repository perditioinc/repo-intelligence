"""Tests for reporium_scoring.cli output format."""

from __future__ import annotations

from reporium_scoring.cli import _format_checks, _print_score, _tick
from reporium_scoring.models import CheckResult, RepoScore


def _make_score(total: int = 75, grade: str = "B", error: str | None = None) -> RepoScore:
    """Build a RepoScore test fixture."""
    checks = [
        CheckResult("readme_exists", 5, True),
        CheckResult("readme_500_chars", 5, False),
    ]
    return RepoScore(
        owner="langchain-ai",
        repo="langchain",
        total=total,
        grade=grade,
        readme_checks=checks,
        activity_checks=[CheckResult("committed_30d", 10, True)],
        community_checks=[CheckResult("has_license", 10, True)],
        ci_checks=[CheckResult("has_workflows", 10, True)],
        error=error,
    )


def test_tick_passed():
    """✓ for passed checks."""
    assert _tick(True) == "✓"


def test_tick_failed():
    """✗ for failed checks."""
    assert _tick(False) == "✗"


def test_format_checks():
    """Format includes check name with symbol."""
    checks = [CheckResult("readme_exists", 5, True), CheckResult("readme_500_chars", 5, False)]
    result = _format_checks(checks)
    assert "✓ readme_exists" in result
    assert "✗ readme_500_chars" in result


def test_print_score_format(capsys):
    """Output contains repo name, score, and grade."""
    score = _make_score()
    _print_score(score)
    captured = capsys.readouterr()
    assert "langchain-ai/langchain" in captured.out
    assert "75/100" in captured.out
    assert "Grade: B" in captured.out


def test_print_score_all_categories(capsys):
    """Output contains all four category lines."""
    _print_score(_make_score())
    captured = capsys.readouterr()
    for label in ["README:", "Activity:", "Community:", "CI:"]:
        assert label in captured.out


def test_print_score_error(capsys):
    """Error score prints ERROR instead of grade table."""
    score = _make_score(total=0, error="connection refused")
    _print_score(score)
    captured = capsys.readouterr()
    assert "ERROR" in captured.out
    assert "connection refused" in captured.out

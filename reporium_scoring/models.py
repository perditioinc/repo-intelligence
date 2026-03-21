"""Data models for repo-intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CheckResult:
    """Result of a single scoring check."""

    name: str
    points: int
    passed: bool
    detail: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "name": self.name,
            "points": self.points,
            "passed": self.passed,
            "detail": self.detail,
        }


@dataclass
class RepoScore:
    """Full scoring result for a repository."""

    owner: str
    repo: str
    total: int
    grade: str
    readme_checks: list[CheckResult] = field(default_factory=list)
    activity_checks: list[CheckResult] = field(default_factory=list)
    community_checks: list[CheckResult] = field(default_factory=list)
    ci_checks: list[CheckResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def readme_score(self) -> int:
        """Sum of passed readme check points."""
        return sum(c.points for c in self.readme_checks if c.passed)

    @property
    def activity_score(self) -> int:
        """Sum of passed activity check points."""
        return sum(c.points for c in self.activity_checks if c.passed)

    @property
    def community_score(self) -> int:
        """Sum of passed community check points."""
        return sum(c.points for c in self.community_checks if c.passed)

    @property
    def ci_score(self) -> int:
        """Sum of passed CI check points."""
        return sum(c.points for c in self.ci_checks if c.passed)

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "owner": self.owner,
            "repo": self.repo,
            "total": self.total,
            "grade": self.grade,
            "readme_score": self.readme_score,
            "activity_score": self.activity_score,
            "community_score": self.community_score,
            "ci_score": self.ci_score,
            "readme_checks": [c.to_dict() for c in self.readme_checks],
            "activity_checks": [c.to_dict() for c in self.activity_checks],
            "community_checks": [c.to_dict() for c in self.community_checks],
            "ci_checks": [c.to_dict() for c in self.ci_checks],
            "error": self.error,
        }

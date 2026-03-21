"""repo-intelligence: Score any GitHub repo 0-100."""

from .scorer import score_repo, score_repos_batch

__all__ = ["score_repo", "score_repos_batch"]

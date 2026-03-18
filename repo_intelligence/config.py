"""Configuration for repo-intelligence."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Runtime configuration."""

    gh_token: str
    concurrency: int


def load_config() -> Config:
    """Load configuration from environment variables.

    Raises:
        ValueError: If GH_TOKEN is not set.
    """
    token = os.getenv("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN environment variable is required")
    return Config(
        gh_token=token,
        concurrency=int(os.getenv("CONCURRENCY_CHECKS", "10")),
    )

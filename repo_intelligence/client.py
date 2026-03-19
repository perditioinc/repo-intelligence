"""Async GitHub API client with retry and shared httpx session."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubClient:
    """Async HTTP client for the GitHub REST API with retry on 429/502/503."""

    def __init__(self, token: str, http: Optional[httpx.AsyncClient] = None) -> None:
        """Initialize the client.

        Args:
            token: GitHub personal access token.
            http: Optional shared httpx.AsyncClient for testing or connection reuse.
        """
        self._token = token
        self._http = http
        self._owns_client = http is None

    async def __aenter__(self) -> "GitHubClient":
        """Create the HTTP client if not provided."""
        if self._owns_client:
            self._http = httpx.AsyncClient(timeout=15, follow_redirects=True)
        return self

    async def __aexit__(self, *_: object) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client and self._http:
            await self._http.aclose()

    async def get(self, path: str, attempt: int = 0) -> Optional[dict[str, Any]]:
        """Perform a GET request against the GitHub REST API.

        Args:
            path: API path, e.g. '/repos/owner/repo'.
            attempt: Current retry attempt (0-indexed).

        Returns:
            Parsed JSON dict, or None if the resource does not exist (404).

        Raises:
            httpx.HTTPStatusError: On non-retryable errors after max attempts.
        """
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{GITHUB_API}{path}"
        try:
            resp = await self._http.get(url, headers=headers)
        except httpx.RequestError as exc:
            if attempt >= 3:
                raise
            wait = 2**attempt
            logger.warning("Request error (attempt %d): %s — retry in %ds", attempt + 1, exc, wait)
            await asyncio.sleep(wait)
            return await self.get(path, attempt + 1)

        if resp.status_code == 404:
            return None
        if resp.status_code in (429, 502, 503):
            if attempt >= 3:
                resp.raise_for_status()
            wait = 2**attempt
            logger.warning(
                "HTTP %d (attempt %d) — retry in %ds", resp.status_code, attempt + 1, wait
            )
            await asyncio.sleep(wait)
            return await self.get(path, attempt + 1)

        resp.raise_for_status()
        return resp.json()

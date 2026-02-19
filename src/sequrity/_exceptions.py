"""Custom exception hierarchy for the Sequrity SDK."""

from __future__ import annotations

import httpx


class SequrityError(Exception):
    """Base exception for all Sequrity SDK errors."""


class SequrityAPIError(SequrityError):
    """HTTP error returned by the Sequrity API.

    Attributes:
        status_code: HTTP status code (e.g. 400, 401, 500).
        message: Human-readable error description.
        response: The raw httpx.Response for advanced inspection.
    """

    def __init__(self, status_code: int, message: str, response: httpx.Response):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"[{status_code}] {message}")

    @classmethod
    def from_response(cls, response: httpx.Response) -> SequrityAPIError:
        """Construct from an httpx response with a non-2xx status code."""
        try:
            body = response.json()
            message = body.get("detail", body.get("message", response.text))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
        return cls(status_code=response.status_code, message=str(message), response=response)


class SequrityValidationError(SequrityError):
    """Request payload failed Pydantic validation."""


class SequrityConnectionError(SequrityError):
    """Network or connection failure."""

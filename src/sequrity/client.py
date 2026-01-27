"""Sequrity API client module.

This module provides the main client class for interacting with the Sequrity API.
"""

import httpx

from .constants import SEQURITY_API_URL
from .control.wrapper import ControlApiWrapper


class SequrityClient:
    """Main client for interacting with the Sequrity API.

    The SequrityClient provides a high-level interface for accessing Sequrity's
    security features, including chat completion with security policies and
    LangGraph integration.

    Attributes:
        control: The Control API wrapper for chat completions and LangGraph operations.
    """

    def __init__(self, api_key: str, base_url: str | None = None, timeout: int = 300):
        """Initialize the Sequrity client.

        Args:
            api_key: Your Sequrity API key for authentication.
            base_url: Optional custom base URL for the Sequrity API.
                Defaults to the production Sequrity API URL.
            timeout: Request timeout in seconds. Defaults to 300.
        """
        self._api_key = api_key
        self._base_url = base_url or SEQURITY_API_URL
        self._client = httpx.Client(timeout=timeout)
        self.control = ControlApiWrapper(client=self._client, base_url=self._base_url, api_key=self._api_key)

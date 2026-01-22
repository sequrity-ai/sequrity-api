"""Sequrity API client module.

This module provides the main client class for interacting with the Sequrity API.
"""

import httpx

from .constants import SEQURITY_API_URL
from .control.wrapper import ControlAPIWrapper


class SequrityClient:
    """Main client for interacting with the Sequrity API.

    The SequrityClient provides a high-level interface for accessing Sequrity's
    security features, including chat completion with security policies and
    LangGraph integration.

    Attributes:
        control: The Control API wrapper for chat completions and LangGraph operations.

    Example:
        ```python
        from sequrity_api import SequrityClient
        from sequrity_api.types.control.headers import FeaturesHeader, SecurityPolicyHeader

        client = SequrityClient(api_key="your-sequrity-api-key")

        # Create feature and policy headers
        features = FeaturesHeader.create_single_llm_headers()
        policy = SecurityPolicyHeader.create_default()

        # Use the control API for secure chat completions
        response = client.control.create_chat_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-4o",
            llm_api_key="your-openai-api-key",
            service_provider="openai",
        )
        ```
    """

    def __init__(self, api_key: str, base_url: str | None = None, timeout: int = 30):
        """Initialize the Sequrity client.

        Args:
            api_key: Your Sequrity API key for authentication.
            base_url: Optional custom base URL for the Sequrity API.
                Defaults to the production Sequrity API URL.
            timeout: Request timeout in seconds. Defaults to 30.
        """
        self._api_key = api_key
        self._base_url = base_url or SEQURITY_API_URL
        self._client = httpx.Client(timeout=timeout)
        self.control = ControlAPIWrapper(client=self._client, base_url=self._base_url, api_key=self._api_key)

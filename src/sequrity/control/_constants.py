"""URL builders and API constants for Sequrity Control."""

from __future__ import annotations

from ..types.enums import LlmServiceProvider, LlmServiceProviderStr, RestApiType

SEQURITY_BASE_URL = "https://api.sequrity.ai"
SEQURITY_API_VERSION = "v1"

# URL suffix for each REST API type
_REST_API_SUFFIX: dict[RestApiType, str] = {
    RestApiType.CHAT_COMPLETIONS: "chat/completions",
    RestApiType.MESSAGES: "messages",
    RestApiType.RESPONSES: "responses",
}

# Policy generation: request type -> provider slug (None = default route)
_POLICY_GEN_PROVIDER: dict[str, str | None] = {
    "oai_chat_completion": "openai",
    "openrouter_chat_completion": None,
    "anthropic_messages": "anthropic",
    "sequrity_azure_chat_completion": "sequrity_azure",
    "sequrity_azure_responses": "sequrity_azure",
}


def build_policy_gen_url(
    base_url: str,
    request_type: str,
    version: str = SEQURITY_API_VERSION,
) -> str:
    """Build the policy generation endpoint URL for a given request type.

    Routes to ``{base}/control/policy-gen/{provider}/{version}/generate`` when
    the request type maps to a provider, or
    ``{base}/control/policy-gen/{version}/generate`` for the default route.
    """
    provider = _POLICY_GEN_PROVIDER.get(request_type)
    if provider:
        return f"{base_url}/control/policy-gen/{provider}/{version}/generate"
    return f"{base_url}/control/policy-gen/{version}/generate"


def build_control_base_url(
    base_url: str,
    endpoint_type: str,
    provider: LlmServiceProvider | LlmServiceProviderStr | None = None,
    version: str = SEQURITY_API_VERSION,
) -> str:
    """Build URL up to version segment.

    Returns ``{base}/control/{endpoint_type}/{provider}/{version}`` when a
    provider is given, or ``{base}/control/{endpoint_type}/{version}`` otherwise.

    Used by integration clients (OpenAI SDK, LangChain) that append their own
    API paths to the base URL.
    """
    if provider:
        return f"{base_url}/control/{endpoint_type}/{provider}/{version}"
    return f"{base_url}/control/{endpoint_type}/{version}"


def build_control_url(
    base_url: str,
    endpoint_type: str,
    rest_api_type: RestApiType,
    provider: LlmServiceProvider | LlmServiceProviderStr | None = None,
    version: str = SEQURITY_API_VERSION,
) -> str:
    """Build complete endpoint URL.

    Returns ``{base}/control/{endpoint_type}/{provider?}/{version}/{suffix}``.

    Args:
        base_url: Sequrity API base URL.
        endpoint_type: Endpoint type (chat, code, agent, lang-graph).
        rest_api_type: REST API style (chat_completions, messages, or responses).
        provider: LLM provider slug, or None for the provider-less default route.
        version: API version string.
    """
    base = build_control_base_url(base_url, endpoint_type, provider, version)
    return f"{base}/{_REST_API_SUFFIX[rest_api_type]}"


def build_sequrity_headers(
    api_key: str,
    *,
    llm_api_key: str | None = None,
    features: str | None = None,
    policy: str | None = None,
    config: str | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    """Build Sequrity API request headers.

    Header model values should be pre-serialized via
    ``dump_for_headers(mode="json_str")``.
    """
    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if llm_api_key:
        headers["X-Api-Key"] = llm_api_key
    if features:
        headers["X-Features"] = features
    if policy:
        headers["X-Policy"] = policy
    if config:
        headers["X-Config"] = config
    if session_id:
        headers["X-Session-ID"] = session_id
    return headers

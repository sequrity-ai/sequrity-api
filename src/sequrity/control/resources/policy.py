"""Policy generation resource."""

from __future__ import annotations

from pydantic import TypeAdapter

from ..._sentinel import NOT_GIVEN, _NotGiven
from .._transport import ControlAsyncTransport, ControlSyncTransport
from ..types.policy_gen import PolicyGenRequest, PolicyGenResponse

_PolicyGenRequestAdapter = TypeAdapter(PolicyGenRequest)


class PolicyResource:
    """Policy generation — ``client.control.policy``."""

    def __init__(self, transport: ControlSyncTransport) -> None:
        self._transport = transport

    def generate(
        self,
        request: PolicyGenRequest | dict,
        *,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
    ) -> PolicyGenResponse:
        """Generate a SQRT security policy from a natural language description.

        Args:
            request: Policy generation request, either as a typed Pydantic model
                or a raw dict. The request must include a ``type`` discriminator
                field to select the tool format variant.
            llm_api_key: Optional LLM provider API key override.

        Returns:
            Parsed ``PolicyGenResponse`` with generated policies and usage info.
        """
        # Validate and serialize
        if isinstance(request, dict):
            validated = _PolicyGenRequestAdapter.validate_python(request)
        else:
            validated = request
        payload = validated.model_dump(exclude_none=True)

        url = self._transport.build_policy_gen_url(validated.type)

        # Policy gen uses simpler headers: no features/policy/config/session
        response = self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=None,
            security_policy=None,
            fine_grained_config=None,
            include_session=False,
        )

        return PolicyGenResponse.model_validate(response.json())


class AsyncPolicyResource:
    """Async variant of :class:`PolicyResource`."""

    def __init__(self, transport: ControlAsyncTransport) -> None:
        self._transport = transport

    async def generate(
        self,
        request: PolicyGenRequest | dict,
        *,
        llm_api_key: str | None | _NotGiven = NOT_GIVEN,
    ) -> PolicyGenResponse:
        """Async variant of :meth:`PolicyResource.generate`."""
        if isinstance(request, dict):
            validated = _PolicyGenRequestAdapter.validate_python(request)
        else:
            validated = request
        payload = validated.model_dump(exclude_none=True)

        url = self._transport.build_policy_gen_url(validated.type)

        response = await self._transport.request(
            url=url,
            payload=payload,
            llm_api_key=llm_api_key,
            features=None,
            security_policy=None,
            fine_grained_config=None,
            include_session=False,
        )

        return PolicyGenResponse.model_validate(response.json())

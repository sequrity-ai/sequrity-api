"""Immutable configuration for the Sequrity Control product."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types.enums import EndpointType
from ..types.enums import LlmServiceProvider, LlmServiceProviderStr

if TYPE_CHECKING:
    from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


@dataclass(frozen=True)
class ControlConfig:
    """Stores default values for Sequrity Control API requests.

    Resources and the transport layer read from this to fill in values that
    the caller did not explicitly provide on a per-request basis.

    All fields are optional — when omitted, per-request overrides or server
    defaults are used instead.
    """

    llm_api_key: str | None = None
    provider: LlmServiceProvider | LlmServiceProviderStr | None = None
    endpoint_type: str = field(default=EndpointType.CHAT)
    features: FeaturesHeader | None = None
    security_policy: SecurityPolicyHeader | None = None
    fine_grained_config: FineGrainedConfigHeader | None = None

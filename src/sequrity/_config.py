"""Immutable client configuration holding default values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


@dataclass(frozen=True)
class ClientConfig:
    """Stores default values set at client creation time.

    Resources and the transport layer read from this to fill in values that
    the caller did not explicitly provide on a per-request basis.
    """

    api_key: str
    base_url: str
    llm_api_key: str | None
    provider: str | None
    endpoint_type: str
    features: FeaturesHeader | None
    security_policy: SecurityPolicyHeader | None
    fine_grained_config: FineGrainedConfigHeader | None

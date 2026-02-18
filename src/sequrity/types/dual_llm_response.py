"""Dual-LLM response content types.

These types represent the JSON schema of the ``content`` field in assistant
messages returned by Sequrity Control's dual-LLM architecture.  They are
**not** LangGraph-specific — any dual-LLM session produces responses in this
format.

Typical usage::

    from sequrity.types.dual_llm_response import ResponseContentJsonSchema

    parsed = ResponseContentJsonSchema.parse_json_safe(
        response.choices[0].message.content
    )
    if parsed.status == "success":
        print(parsed.final_return_value.value)
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MetaData(BaseModel):
    """Metadata associated with a value for Sequrity Control's policy enforcement system.

    Every value flowing through the dual-LLM interpreter carries metadata that
    records *who* produced it, *who* may consume it, and arbitrary *tags* for
    policy matching.
    """

    producers: set[str] = Field(default_factory=set)
    consumers: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)

    model_config = ConfigDict(extra="forbid")


class ValueWithMeta(BaseModel):
    """Python value wrapper with metadata for Sequrity Control's policy enforcement system."""

    value: Any
    meta: MetaData = Field(default_factory=MetaData)

    model_config = ConfigDict(extra="forbid")


class ErrorInfo(BaseModel):
    """Represents error information in a dual-LLM response.

    When the server serialises an error for the user, it simplifies the
    internal ``StateExecutionError`` into this flat structure.
    """

    code: str
    message: str


class ResponseContentJsonSchema(BaseModel):
    """Response content of a dual-LLM session.

    Parses the ``content`` field of the assistant message returned by
    Sequrity Control in dual-LLM mode.  The JSON looks like::

        {
            "status": "success",
            "final_return_value": {"value": "...", "meta": {...}},
            "program": "...",
            ...
        }

    Use :meth:`parse_json_safe` for lenient parsing that never raises.
    """

    status: Literal["success", "failure", "unknown"]
    final_return_value: ValueWithMeta | None = Field(default=None)
    error: ErrorInfo | None = Field(default=None)
    program: str | None = Field(default=None)
    namespace_snapshot: dict[str, ValueWithMeta] | None = Field(default=None)
    session_meta: ValueWithMeta | None = Field(default=None)
    policy_check_history: list[dict[str, Any]] | None = Field(default=None)
    message_history_mismatch_detected: bool | None = Field(default=None)
    raw: str | None = Field(default=None)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def parse_json_safe(cls, data: str) -> ResponseContentJsonSchema:
        """Parse JSON data safely, returning an ``unknown`` status if parsing fails."""
        try:
            validated = cls.model_validate_json(data)
        except Exception:
            validated = cls(status="unknown", raw=data)
        return validated

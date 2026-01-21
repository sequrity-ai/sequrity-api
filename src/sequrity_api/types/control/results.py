import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .value_with_meta import ValueWithMeta


class ErrorInfo(BaseModel):
    error_code: str
    error_message: str


class ResponseContentJsonSchema(BaseModel):
    """
    Return value of a Single-LLM/Dual-LLM system
    """

    status: Literal["success", "failure", "unknown"]
    final_return_value: ValueWithMeta | None = Field(default=None)
    error: ErrorInfo | None = Field(default=None)
    program: str | None = Field(default=None)
    namespace_screenshot: dict[str, ValueWithMeta] | None = Field(default=None)
    raw: str | None = Field(default=None)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def parse_raw(cls, data: str) -> "ResponseContentJsonSchema":
        try:
            validated = cls.model_validate_json(data)
        except Exception as e:
            validated = cls(status="unknown", raw=data)
        return validated

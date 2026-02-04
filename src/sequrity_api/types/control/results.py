from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .value_with_meta import ValueWithMeta


class ErrorInfo(BaseModel):
    """
    Represents error information in the response.
    """

    code: str
    message: str


class ResponseContentJsonSchema(BaseModel):
    """
    ResponseContent (sequrity_api.types.chat_completion.response.ResponseMessage.content) of a Dual-LLM system.
    """

    status: Literal["success", "failure", "unknown"]
    final_return_value: ValueWithMeta | None = Field(default=None)
    error: ErrorInfo | None = Field(default=None)
    program: str | None = Field(default=None)
    namespace_screenshot: dict[str, ValueWithMeta] | None = Field(default=None)
    raw: str | None = Field(default=None)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def parse_json_safe(cls, data: str) -> "ResponseContentJsonSchema":
        """Parse JSON data safely, returning an unknown status if parsing fails."""
        try:
            validated = cls.model_validate_json(data)
        except Exception:
            validated = cls(status="unknown", raw=data)
        return validated

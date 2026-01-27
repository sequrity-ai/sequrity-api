from pydantic import Field

from ..chat_completion.request import ChatCompletionRequest
from ..chat_completion.response import ChatCompletionResponse
from .value_with_meta import ValueWithMeta


class LangGraphChatCompletionRequest(ChatCompletionRequest):
    user_provided_program: str | None = Field(
        default=None,
        description="The user-provided Python program (as JSON string) to execute. This replaces messages in traditional chat completion requests.",
    )
    predefined_vars_with_meta: dict[str, ValueWithMeta] | None = Field(
        default=None,
        description="Predefined variables with meta for the interpreter.",
    )


class LangGraphChatCompletionResponse(ChatCompletionResponse):
    pass

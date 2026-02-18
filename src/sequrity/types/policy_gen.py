"""Policy Generation types.

This module provides Pydantic models for constructing policy generation requests
and parsing responses from Sequrity's Policy Generation API.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .chat_completion.request import Tool as ChatCompletionTool
from .messages.request import ToolParam as AnthropicToolParam

# =============================================================================
# Internal Tool Names
# =============================================================================

InternalToolName = Literal["parse_with_ai", "verify_hypothesis", "set_policy", "complete_turn"]


# =============================================================================
# Policy Generation Request Types
# =============================================================================


class PolicyGenRequestBase(BaseModel):
    """Base fields shared by all policy generation request variants."""

    model: str = Field(..., description="The model to use for policy generation.")
    description: str = Field(..., description="A description of the policy to generate in natural language.")
    policy_lang: Literal["sqrt"] = Field(
        default="sqrt",
        description="The policy language to generate the policy in.",
    )
    n_retries: int = Field(
        default=3,
        description="The number of times to retry policy generation if it fails or the generated policy is invalid.",
        ge=0,
    )
    internal_tool_names: list[InternalToolName] = Field(
        default_factory=list, description="The list of internal tools to consider during policy generation."
    )


class PolicyGenRequestOpenAiChatCompletion(PolicyGenRequestBase):
    """Policy generation request using OpenAI Chat Completions tool format."""

    type: Literal["oai_chat_completion"] = Field(default="oai_chat_completion")
    tools: list[ChatCompletionTool] = Field(
        default_factory=list,
        description="The list of tools in OpenAI function tool format.",
    )

    model_config = ConfigDict(extra="forbid")


class PolicyGenRequestOpenRouterChatCompletion(PolicyGenRequestBase):
    """Policy generation request using OpenRouter Chat Completions tool format."""

    type: Literal["openrouter_chat_completion"] = Field(default="openrouter_chat_completion")
    tools: list[ChatCompletionTool] = Field(
        default_factory=list,
        description="The list of tools in OpenRouter function tool format.",
    )

    model_config = ConfigDict(extra="forbid")


class PolicyGenRequestAnthropicMessages(PolicyGenRequestBase):
    """Policy generation request using Anthropic Messages tool format."""

    type: Literal["anthropic_messages"] = Field(default="anthropic_messages")
    tools: list[AnthropicToolParam] = Field(
        default_factory=list,
        description="The list of tools in Anthropic Messages tool format.",
    )

    model_config = ConfigDict(extra="forbid")


class PolicyGenRequestOaiResponses(PolicyGenRequestBase):
    """Policy generation request using OpenAI Responses tool format.

    .. note:: Not yet supported by the server. Retained for forward compatibility.
    """

    type: Literal["oai_responses"] = Field(default="oai_responses")
    tools: list[dict[str, Any]] = Field(
        default_factory=list,
        description="The list of tools in OpenAI Responses format.",
    )

    model_config = ConfigDict(extra="forbid")


class PolicyGenRequestSequrityAzureChatCompletion(PolicyGenRequestBase):
    """Policy generation request using Sequrity Azure Chat Completions tool format."""

    type: Literal["sequrity_azure_chat_completion"] = Field(default="sequrity_azure_chat_completion")
    tools: list[ChatCompletionTool] = Field(
        default_factory=list,
        description="The list of tools in Sequrity Azure function tool format.",
    )

    model_config = ConfigDict(extra="forbid")


class PolicyGenRequestSequrityAzureResponses(PolicyGenRequestBase):
    """Policy generation request using Sequrity Azure Responses tool format."""

    type: Literal["sequrity_azure_responses"] = Field(default="sequrity_azure_responses")
    tools: list[dict[str, Any]] = Field(
        default_factory=list,
        description="The list of tools in Sequrity Azure Responses format.",
    )

    model_config = ConfigDict(extra="forbid")


PolicyGenRequest = Annotated[
    PolicyGenRequestOpenAiChatCompletion
    | PolicyGenRequestOpenRouterChatCompletion
    | PolicyGenRequestAnthropicMessages
    | PolicyGenRequestSequrityAzureChatCompletion
    | PolicyGenRequestSequrityAzureResponses,
    Field(discriminator="type"),
]


# =============================================================================
# Policy Generation Response
# =============================================================================


class PolicyGenResponse(BaseModel):
    """Response from the policy generation endpoint.

    Contains the generated SQRT policy code and token usage statistics.
    """

    policies: str = Field(..., description="The generated policy or policies in the specified policy language.")
    usage: dict[str, int] = Field(..., description="Token usage for the policy generation request.")

    model_config = ConfigDict(extra="forbid")

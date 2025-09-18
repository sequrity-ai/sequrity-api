from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricProgramSize(BaseModel):
    loc: int = Field(default=0, description="Lines of code", ge=0)


class MetricTokenUsage(BaseModel):
    prompt_tokens: int = Field(default=0, description="Number of prompt tokens", ge=0)
    completion_tokens: int = Field(default=0, description="Number of completion tokens", ge=0)
    total_tokens: int = Field(default=0, description="Total number of tokens", ge=0)


class MetricRuntime(BaseModel):
    start_time: datetime | None = Field(default=None)
    end_time: datetime | None = Field(default=None)
    duration: float = Field(default=0.0, description="Duration in seconds", ge=0)


class SoUsage(BaseModel):
    # to be compatible with OpenAI usage field
    prompt_tokens: int = Field(default=0, description="Number of prompt tokens", ge=0)
    completion_tokens: int = Field(default=0, description="Number of completion tokens", ge=0)
    total_tokens: int = Field(default=0, description="Total number of tokens", ge=0)

    # sequrity specific metrics
    sqrt_program_size: MetricProgramSize = Field(default_factory=lambda: MetricProgramSize())
    sqrt_pllm_token_usage: MetricTokenUsage = Field(default_factory=lambda: MetricTokenUsage())
    sqrt_qllm_token_usage: MetricTokenUsage = Field(default_factory=lambda: MetricTokenUsage())
    sqrt_rllm_token_usage: MetricTokenUsage = Field(default_factory=lambda: MetricTokenUsage())
    sqrt_runtime: MetricRuntime = Field(default_factory=lambda: MetricRuntime())

    model_config = ConfigDict(extra="allow")

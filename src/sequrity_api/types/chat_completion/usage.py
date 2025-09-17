from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricProgramSize(BaseModel):
    loc: int = Field(default=0, description="Lines of code", ge=0)

    def add_codes(self, codes: str):
        self.loc += len(codes.splitlines())

    def reset(self):
        self.loc = 0


class MetricTokenUsage(BaseModel):
    prompt_tokens: int = Field(default=0, description="Number of prompt tokens", ge=0)
    completion_tokens: int = Field(
        default=0, description="Number of completion tokens", ge=0
    )
    total_tokens: int = Field(default=0, description="Total number of tokens", ge=0)

    def reset(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0


class MetricRuntime(BaseModel):
    start_time: datetime | None = Field(default=None)
    end_time: datetime | None = Field(default=None)
    duration: float = Field(default=0.0, description="Duration in seconds", ge=0)

    def tik(self):
        """Start the timer if it is not already running."""
        if self.start_time is None:
            self.start_time = datetime.now()

    def tok(self):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.duration = 0.0


class SoUsage(BaseModel):
    # to be compatible with OpenAI usage field
    prompt_tokens: int = Field(default=0, description="Number of prompt tokens", ge=0)
    completion_tokens: int = Field(
        default=0, description="Number of completion tokens", ge=0
    )
    total_tokens: int = Field(default=0, description="Total number of tokens", ge=0)

    # sequrity specific metrics
    sqrt_program_size: MetricProgramSize = Field(
        default_factory=lambda: MetricProgramSize()
    )
    sqrt_pllm_token_usage: MetricTokenUsage = Field(
        default_factory=lambda: MetricTokenUsage()
    )
    sqrt_qllm_token_usage: MetricTokenUsage = Field(
        default_factory=lambda: MetricTokenUsage()
    )
    sqrt_rllm_token_usage: MetricTokenUsage = Field(
        default_factory=lambda: MetricTokenUsage()
    )
    sqrt_runtime: MetricRuntime = Field(default_factory=lambda: MetricRuntime())

    model_config = ConfigDict(extra="allow")

    def reset(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

        self.sqrt_program_size.reset()
        self.sqrt_qllm_token_usage.reset()
        self.sqrt_pllm_token_usage.reset()
        self.sqrt_rllm_token_usage.reset()
        self.sqrt_runtime.reset()

    def add_tokens(
        self,
        which: Literal["pllm", "qllm", "rllm"],
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ):
        if which == "pllm":
            usage = self.sqrt_pllm_token_usage
        elif which == "qllm":
            usage = self.sqrt_qllm_token_usage
        elif which == "rllm":
            usage = self.sqrt_rllm_token_usage
        else:
            raise ValueError(f"Unknown which: {which}")

        if prompt_tokens is not None:
            usage.prompt_tokens += prompt_tokens
            self.prompt_tokens += prompt_tokens
        if completion_tokens is not None:
            usage.completion_tokens += completion_tokens
            self.completion_tokens += completion_tokens
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens

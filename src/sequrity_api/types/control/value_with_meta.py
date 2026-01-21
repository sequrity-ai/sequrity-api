from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MetaData(BaseModel):
    producers: set[str] = Field(default_factory=set)
    consumers: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)

    model_config = ConfigDict(extra="forbid")


class ValueWithMeta(BaseModel):
    value: Any
    meta: MetaData = Field(default_factory=MetaData)

    model_config = ConfigDict(extra="forbid")

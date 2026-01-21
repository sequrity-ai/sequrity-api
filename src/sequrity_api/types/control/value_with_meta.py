from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


class MetaData(BaseModel):
    producers: set[str] = Field(default_factory=set)
    consumers: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)

    model_config = ConfigDict(extra="forbid")


class ValueWithMeta(BaseModel):
    value: JsonValue
    meta: MetaData = Field(default_factory=MetaData)

    model_config = ConfigDict(extra="forbid")

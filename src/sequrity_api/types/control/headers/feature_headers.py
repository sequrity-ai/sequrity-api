import json
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

OptionalInternalSoToolIdType: TypeAlias = Literal["parse_with_ai", "verify_hypothesis"]
DebugInfoLevel: TypeAlias = Literal["minimal", "normal", "extra"]


class LlmModeFeature(BaseModel):
    feature_name: Literal["Single LLM", "Dual LLM"]
    mode: Literal["standard", "strict", "custom"]

    def dump_for_headers(self) -> dict:
        return {
            "feature_name": self.feature_name,
            "config_json": json.dumps({"mode": self.mode}),
        }


class TaggerFeature(BaseModel):
    feature_name: Literal[
        "Toxicity Filter",
        "PII Redaction",
        "Healthcare Topic Guardrail",
        "Finance Topic Guardrail",
        "Legal Topic Guardrail",
    ]
    threshold: float = Field(default=0.5, description="Detection threshold")
    enabled: bool = Field(default=True, description="Whether the tagger is enabled.")
    # this overrides the threshold value if provided
    mode: Literal["normal", "strict"] | None = Field(default=None, description="Tagger mode which override threshold.")
    tag_name: str | None = Field(default=None, description="Custom tag name for the tagger.")

    def dump_for_headers(self) -> dict:
        config = {
            "feature_name": self.feature_name,
            "config_json": self.model_dump_json(exclude_none=True, exclude={"feature_name"}),
        }
        return config


class ConstraintFeature(BaseModel):
    feature_name: Literal["URL Blocker"]
    name: Literal["url_blocker"]
    enabled: bool = Field(default=True, description="Whether the constraint is enabled.")

    def dump_for_headers(self) -> dict:
        config = {
            "feature_name": self.feature_name,
            "config_json": self.model_dump_json(exclude_none=True, exclude={"feature_name"}),
        }
        return config


class LongProgramSupportFeature(BaseModel):
    feature_name: Literal["Long Program Support"]
    mode: Literal["base", "mid", "long"] = Field(
        default="base", description="The level of long program support, which is used to set gas of interpreter."
    )

    def dump_for_headers(self) -> dict:
        config = {
            "feature_name": self.feature_name,
            "config_json": json.dumps({"mode": self.mode}),
        }
        return config


class FeaturesHeader(BaseModel):
    llm: LlmModeFeature = Field(..., description="LLM mode feature configuration.")
    taggers: list[TaggerFeature] | None = Field(None, description="List of tagger feature configurations.")
    constraints: list[ConstraintFeature] | None = Field(None, description="List of constraint feature configurations.")
    long_program_support: LongProgramSupportFeature | None = Field(
        ..., description="Long program support feature configuration."
    )

    model_config = ConfigDict(extra="forbid")

    def dump_for_headers(self, mode: Literal["json", "json_str"]) -> list[dict] | str:
        features_list = []

        # LLM feature
        features_list.append(self.llm.dump_for_headers())

        # Tagger features
        if self.taggers:
            for tagger in self.taggers:
                features_list.append(tagger.dump_for_headers())

        # Constraint features
        if self.constraints:
            for constraint in self.constraints:
                features_list.append(constraint.dump_for_headers())

        # Long program support feature
        if self.long_program_support:
            features_list.append(self.long_program_support.dump_for_headers())

        if mode == "json":
            return features_list
        elif mode == "json_str":
            return json.dumps(features_list)
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'json' or 'json_str'.")

    @classmethod
    def create_single_llm_headers(
        cls,
        toxicity_filter: bool = False,
        pii_redaction: bool = False,
        healthcare_guardrail: bool = False,
        finance_guardrail: bool = False,
        legal_guardrail: bool = False,
        url_blocker: bool = False,
        long_program_mode: Literal["base", "mid", "long"] = "base",
    ) -> "FeaturesHeader":
        # no need of lang program support for single-llm mode
        taggers = []
        if toxicity_filter:
            taggers.append(TaggerFeature(feature_name="Toxicity Filter"))
        if pii_redaction:
            taggers.append(TaggerFeature(feature_name="PII Redaction"))
        if healthcare_guardrail:
            taggers.append(TaggerFeature(feature_name="Healthcare Topic Guardrail"))
        if finance_guardrail:
            taggers.append(TaggerFeature(feature_name="Finance Topic Guardrail"))
        if legal_guardrail:
            taggers.append(TaggerFeature(feature_name="Legal Topic Guardrail"))
        constraints = []
        if url_blocker:
            constraints.append(ConstraintFeature(feature_name="URL Blocker", name="url_blocker"))
        return cls(
            llm=LlmModeFeature(feature_name="Single LLM", mode="standard"),
            taggers=taggers if taggers else None,
            constraints=constraints if constraints else None,
            long_program_support=LongProgramSupportFeature(feature_name="Long Program Support", mode=long_program_mode),
        )

    @classmethod
    def create_dual_llm_headers(
        cls,
        mode: Literal["standard", "strict", "custom"] = "standard",
        toxicity_filter: bool = False,
        pii_redaction: bool = False,
        healthcare_guardrail: bool = False,
        finance_guardrail: bool = False,
        legal_guardrail: bool = False,
        url_blocker: bool = False,
        long_program_mode: Literal["base", "mid", "long"] = "base",
    ) -> "FeaturesHeader":
        taggers = []
        if toxicity_filter:
            taggers.append(TaggerFeature(feature_name="Toxicity Filter"))
        if pii_redaction:
            taggers.append(TaggerFeature(feature_name="PII Redaction"))
        if healthcare_guardrail:
            taggers.append(TaggerFeature(feature_name="Healthcare Topic Guardrail"))
        if finance_guardrail:
            taggers.append(TaggerFeature(feature_name="Finance Topic Guardrail"))
        if legal_guardrail:
            taggers.append(TaggerFeature(feature_name="Legal Topic Guardrail"))
        constraints = []
        if url_blocker:
            constraints.append(ConstraintFeature(feature_name="URL Blocker", name="url_blocker"))
        return cls(
            llm=LlmModeFeature(feature_name="Dual LLM", mode=mode),
            taggers=taggers if taggers else None,
            constraints=constraints if constraints else None,
            long_program_support=LongProgramSupportFeature(feature_name="Long Program Support", mode=long_program_mode),
        )

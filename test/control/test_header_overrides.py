"""Unit tests for header override merging in dump_for_headers.

These tests verify that the ``overrides`` parameter on
``FeaturesHeader``, ``SecurityPolicyHeader``, and ``FineGrainedConfigHeader``
correctly deep-merges extra/override fields into the serialized output
without requiring ``extra="allow"`` on the Pydantic models.
"""

from __future__ import annotations

import json

import pytest

from sequrity.control.types.headers import (
    FeaturesHeader,
    FineGrainedConfigHeader,
    SecurityPolicyHeader,
    _deep_merge,
)


# ---------------------------------------------------------------------------
# _deep_merge helper
# ---------------------------------------------------------------------------


class TestDeepMerge:
    """Unit tests for the recursive _deep_merge utility."""

    def test_flat_merge(self):
        base = {"a": 1, "b": 2}
        result = _deep_merge(base, {"b": 99, "c": 3})
        assert result == {"a": 1, "b": 99, "c": 3}

    def test_nested_merge(self):
        base = {"outer": {"a": 1, "b": 2}}
        result = _deep_merge(base, {"outer": {"b": 99, "c": 3}})
        assert result == {"outer": {"a": 1, "b": 99, "c": 3}}

    def test_override_replaces_non_dict_with_dict(self):
        base = {"key": "string_value"}
        result = _deep_merge(base, {"key": {"nested": True}})
        assert result == {"key": {"nested": True}}

    def test_override_replaces_dict_with_non_dict(self):
        base = {"key": {"nested": True}}
        result = _deep_merge(base, {"key": "flat_value"})
        assert result == {"key": "flat_value"}

    def test_deeply_nested(self):
        base = {"a": {"b": {"c": 1, "d": 2}}}
        result = _deep_merge(base, {"a": {"b": {"c": 99, "e": 3}}})
        assert result == {"a": {"b": {"c": 99, "d": 2, "e": 3}}}

    def test_empty_override(self):
        base = {"a": 1}
        result = _deep_merge(base, {})
        assert result == {"a": 1}

    def test_mutates_base(self):
        base = {"a": 1}
        _deep_merge(base, {"b": 2})
        assert base == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# FeaturesHeader overrides
# ---------------------------------------------------------------------------


class TestFeaturesHeaderOverrides:
    """Test dump_for_headers(overrides=...) on FeaturesHeader."""

    def test_no_overrides_unchanged(self):
        header = FeaturesHeader.single_llm(toxicity_filter=True)
        without = json.loads(header.dump_for_headers())
        with_none = json.loads(header.dump_for_headers(overrides=None))
        assert without == with_none

    def test_add_new_field(self):
        header = FeaturesHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"custom_field": "value"}))
        assert result["agent_arch"] == "single-llm"
        assert result["custom_field"] == "value"

    def test_override_existing_field(self):
        header = FeaturesHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"agent_arch": "dual-llm"}))
        assert result["agent_arch"] == "dual-llm"

    def test_add_nested_custom_entry(self):
        header = FeaturesHeader.dual_llm(toxicity_filter=True)
        overrides = {
            "content_classifiers": [
                {"name": "custom_classifier", "threshold": 0.8},
            ],
        }
        result = json.loads(header.dump_for_headers(overrides=overrides))
        # Override replaces the list entirely
        assert len(result["content_classifiers"]) == 1
        assert result["content_classifiers"][0]["name"] == "custom_classifier"

    def test_json_mode_returns_dict(self):
        header = FeaturesHeader.single_llm()
        result = header.dump_for_headers(mode="json", overrides={"extra": True})
        assert isinstance(result, dict)
        assert result["extra"] is True

    def test_json_str_mode_returns_string(self):
        header = FeaturesHeader.single_llm()
        result = header.dump_for_headers(mode="json_str", overrides={"extra": True})
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["extra"] is True

    def test_pydantic_validation_still_strict(self):
        """extra='forbid' still blocks unknown fields at construction time."""
        with pytest.raises(Exception):  # ValidationError
            FeaturesHeader(agent_arch="single-llm", bogus_field=123)


# ---------------------------------------------------------------------------
# SecurityPolicyHeader overrides
# ---------------------------------------------------------------------------


class TestSecurityPolicyHeaderOverrides:
    """Test dump_for_headers(overrides=...) on SecurityPolicyHeader."""

    def test_no_overrides_unchanged(self):
        header = SecurityPolicyHeader.single_llm()
        without = json.loads(header.dump_for_headers())
        with_none = json.loads(header.dump_for_headers(overrides=None))
        assert without == with_none

    def test_add_new_top_level_field(self):
        header = SecurityPolicyHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"custom_policy": "enabled"}))
        assert result["mode"] == "standard"
        assert result["custom_policy"] == "enabled"

    def test_override_nested_presets(self):
        header = SecurityPolicyHeader.dual_llm(default_allow=True)
        result = json.loads(header.dump_for_headers(overrides={"presets": {"default_allow": False}}))
        assert result["presets"]["default_allow"] is False
        # Other preset fields should still be present
        assert "enable_non_executable_memory" in result["presets"]

    def test_add_custom_nested_entry(self):
        header = SecurityPolicyHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"presets": {"custom_preset": {"level": "high"}}}))
        assert result["presets"]["custom_preset"] == {"level": "high"}

    def test_override_mode(self):
        header = SecurityPolicyHeader.single_llm(mode="standard")
        result = json.loads(header.dump_for_headers(overrides={"mode": "strict"}))
        assert result["mode"] == "strict"

    def test_json_mode_with_overrides(self):
        header = SecurityPolicyHeader.dual_llm()
        result = header.dump_for_headers(mode="json", overrides={"extra_key": 42})
        assert isinstance(result, dict)
        assert result["extra_key"] == 42


# ---------------------------------------------------------------------------
# FineGrainedConfigHeader overrides
# ---------------------------------------------------------------------------


class TestFineGrainedConfigHeaderOverrides:
    """Test dump_for_headers(overrides=...) on FineGrainedConfigHeader."""

    def test_no_overrides_unchanged(self):
        header = FineGrainedConfigHeader.dual_llm()
        without = json.loads(header.dump_for_headers())
        with_none = json.loads(header.dump_for_headers(overrides=None))
        assert without == with_none

    def test_override_fsm_field(self):
        header = FineGrainedConfigHeader.dual_llm(max_n_turns=5)
        result = json.loads(header.dump_for_headers(overrides={"fsm": {"max_n_turns": 20}}))
        assert result["fsm"]["max_n_turns"] == 20
        # Other FSM fields preserved
        assert "disable_rllm" in result["fsm"]

    def test_add_custom_fsm_entry(self):
        header = FineGrainedConfigHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"fsm": {"custom_setting": "enabled"}}))
        assert result["fsm"]["custom_setting"] == "enabled"
        # Original fields still present
        assert result["fsm"]["max_n_turns"] == 50

    def test_add_new_top_level_section(self):
        header = FineGrainedConfigHeader.single_llm()
        result = json.loads(header.dump_for_headers(overrides={"custom_section": {"key": "value"}}))
        assert result["custom_section"] == {"key": "value"}
        assert "fsm" in result

    def test_override_response_format(self):
        header = FineGrainedConfigHeader.dual_llm(include_program=True)
        result = json.loads(
            header.dump_for_headers(overrides={"response_format": {"include_program": False, "custom_format": True}})
        )
        assert result["response_format"]["include_program"] is False
        assert result["response_format"]["custom_format"] is True

    def test_deeply_nested_prompt_override(self):
        header = FineGrainedConfigHeader.dual_llm(pllm_debug_info_level="minimal")
        result = json.loads(header.dump_for_headers(overrides={"prompt": {"pllm": {"debug_info_level": "extra"}}}))
        assert result["prompt"]["pllm"]["debug_info_level"] == "extra"

    def test_json_mode_with_overrides(self):
        header = FineGrainedConfigHeader.dual_llm()
        result = header.dump_for_headers(mode="json", overrides={"fsm": {"max_n_turns": 99}})
        assert isinstance(result, dict)
        assert result["fsm"]["max_n_turns"] == 99

    def test_pydantic_validation_still_strict(self):
        """extra='forbid' still blocks unknown fields at construction time."""
        with pytest.raises(Exception):  # ValidationError
            FineGrainedConfigHeader(fsm=None, bogus_field=True)

"""Tests for the header configuration classes."""

import json

import pytest

from sequrity.control.types.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader


class TestFeaturesHeader:
    """Test FeaturesHeader factory methods and serialization."""

    def test_single_llm_default(self):
        header = FeaturesHeader.single_llm()
        assert header.llm.feature_name == "Single LLM"
        assert header.llm.mode == "standard"
        assert header.taggers is None
        assert header.constraints is None

    def test_single_llm_with_taggers(self):
        header = FeaturesHeader.single_llm(toxicity_filter=True, pii_redaction=True)
        assert len(header.taggers) == 2
        names = [t.feature_name for t in header.taggers]
        assert "Toxicity Filter" in names
        assert "PII Redaction" in names

    def test_single_llm_with_constraints(self):
        header = FeaturesHeader.single_llm(url_blocker=True)
        assert len(header.constraints) == 1
        assert header.constraints[0].feature_name == "URL Blocker"

    def test_dual_llm_default(self):
        header = FeaturesHeader.dual_llm()
        assert header.llm.feature_name == "Dual LLM"
        assert header.llm.mode == "standard"

    def test_dual_llm_strict_mode(self):
        header = FeaturesHeader.dual_llm(mode="strict")
        assert header.llm.mode == "strict"

    def test_dual_llm_long_program_mode(self):
        header = FeaturesHeader.dual_llm(long_program_mode="long")
        assert header.long_program_support.mode == "long"

    def test_dump_for_headers_json(self):
        header = FeaturesHeader.single_llm()
        result = header.dump_for_headers(mode="json")
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0]["feature_name"] == "Single LLM"

    def test_dump_for_headers_json_str(self):
        header = FeaturesHeader.single_llm()
        result = header.dump_for_headers(mode="json_str")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_dump_for_headers_invalid_mode(self):
        header = FeaturesHeader.single_llm()
        with pytest.raises(ValueError):
            header.dump_for_headers(mode="invalid")


class TestSecurityPolicyHeader:
    """Test SecurityPolicyHeader factory methods and serialization."""

    def test_single_llm_default(self):
        header = SecurityPolicyHeader.single_llm()
        assert header.language == "sqrt-lite"
        assert header.auto_gen is False
        assert header.internal_policy_preset.default_allow is True
        assert header.internal_policy_preset.enable_non_executable_memory is False

    def test_single_llm_with_codes(self):
        codes = 'tool "test" { must allow always; }'
        header = SecurityPolicyHeader.single_llm(codes=codes)
        assert header.codes == codes

    def test_dual_llm_default(self):
        header = SecurityPolicyHeader.dual_llm()
        assert header.language == "sqrt-lite"
        assert header.internal_policy_preset.enable_non_executable_memory is True

    def test_dual_llm_auto_gen(self):
        header = SecurityPolicyHeader.dual_llm(auto_gen=True)
        assert header.auto_gen is True

    def test_dual_llm_branching_policy(self):
        header = SecurityPolicyHeader.dual_llm(
            branching_meta_policy_mode="allow",
            branching_meta_policy_tags=("tag1", "tag2"),
        )
        preset = header.internal_policy_preset
        assert preset.branching_meta_policy.mode == "allow"
        assert preset.branching_meta_policy.tags == ("tag1", "tag2")

    def test_dump_for_headers_json(self):
        header = SecurityPolicyHeader.single_llm()
        result = header.dump_for_headers(mode="json")
        assert isinstance(result, dict)
        assert "language" in result

    def test_dump_for_headers_json_str(self):
        header = SecurityPolicyHeader.single_llm()
        result = header.dump_for_headers(mode="json_str")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "language" in parsed

    def test_dump_for_headers_invalid_mode(self):
        header = SecurityPolicyHeader.single_llm()
        with pytest.raises(ValueError):
            header.dump_for_headers(mode="invalid")


class TestFineGrainedConfigHeader:
    """Test FineGrainedConfigHeader factory methods and serialization."""

    def test_single_llm_default(self):
        header = FineGrainedConfigHeader.single_llm()
        assert header.min_num_tools_for_filtering == 10
        assert header.clear_session_meta == "never"

    def test_dual_llm_default(self):
        header = FineGrainedConfigHeader.dual_llm()
        assert header.max_pllm_attempts == 4
        assert header.merge_system_messages is True
        assert header.cache_tool_result == "deterministic-only"

    def test_dual_llm_custom_attempts(self):
        header = FineGrainedConfigHeader.dual_llm(max_pllm_attempts=8)
        assert header.max_pllm_attempts == 8

    def test_dual_llm_disable_rllm(self):
        header = FineGrainedConfigHeader.dual_llm(disable_rllm=True)
        assert header.disable_rllm is True

    def test_dual_llm_response_format(self):
        header = FineGrainedConfigHeader.dual_llm(
            response_format_include_program=True,
            response_format_include_policy_check_history=True,
        )
        assert header.response_format.include_program is True
        assert header.response_format.include_policy_check_history is True

    def test_dump_for_headers_json(self):
        header = FineGrainedConfigHeader.dual_llm()
        result = header.dump_for_headers(mode="json")
        assert isinstance(result, dict)

    def test_dump_for_headers_json_str(self):
        header = FineGrainedConfigHeader.dual_llm()
        result = header.dump_for_headers(mode="json_str")
        assert isinstance(result, str)
        json.loads(result)  # should not raise

    def test_dump_for_headers_invalid_mode(self):
        header = FineGrainedConfigHeader.dual_llm()
        with pytest.raises(ValueError):
            header.dump_for_headers(mode="invalid")

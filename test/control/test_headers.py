"""Tests for header validation via the /control/v1/validate-headers endpoint.

Dumps each header class with dump_for_headers() and sends the serialized
JSON strings to the server for validation.
"""

from typing import Literal

import httpx
import pytest

from sequrity.types.headers import (
    ConstraintConfig,
    ControlFlowMetaPolicy,
    FeaturesHeader,
    FineGrainedConfigHeader,
    FsmOverrides,
    InternalPolicyPresets,
    PllmPromptOverrides,
    PolicyCode,
    PromptOverrides,
    ResponseFormatOverrides,
    SecurityPolicyHeader,
    TaggerConfig,
)
from sequrity_unittest.config import get_test_config

VALIDATE_HEADERS_PATH = "/control/v1/validate-headers"


class TestFeaturesHeader:
    """Validate X-Features header via the endpoint."""

    def setup_method(self):
        test_config = get_test_config()
        self.url = f"{test_config.base_url.rstrip('/')}{VALIDATE_HEADERS_PATH}"
        self.client = httpx.Client(timeout=30)

    def teardown_method(self):
        self.client.close()

    def _validate(self, header: FeaturesHeader) -> dict:
        resp = self.client.post(self.url, json={"x_features": header.dump_for_headers()})
        assert resp.status_code == 200
        return resp.json()["x_features"]

    def test_single_llm_default(self):
        result = self._validate(FeaturesHeader.single_llm())
        assert result["valid"] is True
        assert result["normalized"]["agent_arch"] == "single-llm"

    def test_single_llm_with_taggers(self):
        header = FeaturesHeader.single_llm(toxicity_filter=True, pii_redaction=True)
        result = self._validate(header)
        assert result["valid"] is True
        names = [c["name"] for c in result["normalized"]["content_classifiers"]]
        assert "toxicity_filter" in names
        assert "pii_redaction" in names

    def test_single_llm_with_constraints(self):
        header = FeaturesHeader.single_llm(url_blocker=True)
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["content_blockers"][0]["name"] == "url_blocker"

    def test_dual_llm_default(self):
        result = self._validate(FeaturesHeader.dual_llm())
        assert result["valid"] is True
        assert result["normalized"]["agent_arch"] == "dual-llm"

    def test_dual_llm_with_classifiers_and_blockers(self):
        header = FeaturesHeader.dual_llm(
            toxicity_filter=True,
            healthcare_guardrail=True,
            url_blocker=True,
            file_blocker=True,
        )
        result = self._validate(header)
        assert result["valid"] is True
        assert len(result["normalized"]["content_classifiers"]) == 2
        assert len(result["normalized"]["content_blockers"]) == 2

    def test_all_classifiers_and_blockers(self):
        header = FeaturesHeader.single_llm(
            toxicity_filter=True,
            pii_redaction=True,
            healthcare_guardrail=True,
            finance_guardrail=True,
            url_blocker=True,
        )
        result = self._validate(header)
        assert result["valid"] is True
        classifier_names = [c["name"] for c in result["normalized"]["content_classifiers"]]
        assert "toxicity_filter" in classifier_names
        assert "pii_redaction" in classifier_names
        assert "healthcare_topic_guardrail" in classifier_names
        assert "finance_topic_guardrail" in classifier_names

    def test_custom_tagger_thresholds(self):
        header = FeaturesHeader(
            agent_arch="dual-llm",
            content_classifiers=[
                TaggerConfig(name="toxicity_filter", threshold=0.7, mode="normal"),
                TaggerConfig(name="pii_redaction", threshold=0.6, mode="strict"),
            ],
            content_blockers=[
                ConstraintConfig(name="url_blocker"),
            ],
        )
        result = self._validate(header)
        assert result["valid"] is True

    def test_invalid_agent_arch(self):
        resp = self.client.post(self.url, json={"x_features": '{"agent_arch": "triple-llm"}'})
        assert resp.status_code == 200
        result = resp.json()["x_features"]
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_extra_field_rejected(self):
        resp = self.client.post(self.url, json={"x_features": '{"agent_arch": "single-llm", "unknown_field": 123}'})
        assert resp.status_code == 200
        result = resp.json()["x_features"]
        assert result["valid"] is False

    def test_invalid_json(self):
        resp = self.client.post(self.url, json={"x_features": "not valid json{{{"})
        assert resp.status_code == 200
        result = resp.json()["x_features"]
        assert result["valid"] is False
        assert any("Invalid JSON" in e for e in result["errors"])


class TestSecurityPolicyHeader:
    """Validate X-Policy header via the endpoint."""

    def setup_method(self):
        test_config = get_test_config()
        self.url = f"{test_config.base_url.rstrip('/')}{VALIDATE_HEADERS_PATH}"
        self.client = httpx.Client(timeout=30)

    def teardown_method(self):
        self.client.close()

    def _validate(self, header: SecurityPolicyHeader) -> dict:
        resp = self.client.post(self.url, json={"x_policy": header.dump_for_headers()})
        assert resp.status_code == 200
        return resp.json()["x_policy"]

    def test_single_llm_default(self):
        result = self._validate(SecurityPolicyHeader.single_llm())
        assert result["valid"] is True
        assert result["normalized"]["mode"] == "standard"

    def test_single_llm_with_codes(self):
        codes = 'tool "test" { must allow always; }'
        header = SecurityPolicyHeader.single_llm(codes=codes)
        result = self._validate(header)
        assert result["valid"] is True

    def test_dual_llm_default(self):
        result = self._validate(SecurityPolicyHeader.dual_llm())
        assert result["valid"] is True
        assert result["normalized"]["mode"] == "standard"

    def test_dual_llm_auto_gen(self):
        header = SecurityPolicyHeader.dual_llm(auto_gen=True)
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["auto_gen"] is True

    def test_dual_llm_branching_policy(self):
        header = SecurityPolicyHeader.dual_llm(
            branching_meta_policy_mode="allow",
            branching_meta_policy_tags={"tag1", "tag2"},
        )
        result = self._validate(header)
        assert result["valid"] is True

    @pytest.mark.parametrize("mode", ["standard", "strict", "custom"])
    def test_dual_llm_modes(self, mode: Literal["standard", "strict", "custom"]):
        header = SecurityPolicyHeader.dual_llm(
            mode=mode,
            codes="",
            auto_gen=False,
            fail_fast=True,
            default_allow=True,
            enable_non_executable_memory=True,
        )
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["mode"] == mode

    def test_all_entries_set(self):
        header = SecurityPolicyHeader(
            mode="standard",
            codes=PolicyCode(),
            auto_gen=False,
            fail_fast=True,
            presets=InternalPolicyPresets(
                default_allow=True,
                enable_non_executable_memory=True,
                branching_meta_policy=ControlFlowMetaPolicy(
                    mode="deny",
                    producers={"test_producer"},
                    tags={"__non_executable", "__tool/parse_with_ai"},
                    consumers={"test_consumer"},
                ),
                enable_llm_blocked_tag=False,
                llm_blocked_tag_enforcement_level="hard",
            ),
        )
        result = self._validate(header)
        assert result["valid"] is True

    def test_invalid_mode(self):
        resp = self.client.post(self.url, json={"x_policy": '{"mode": "ultra-strict"}'})
        assert resp.status_code == 200
        result = resp.json()["x_policy"]
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_extra_field_rejected(self):
        resp = self.client.post(self.url, json={"x_policy": '{"mode": "standard", "bogus": true}'})
        assert resp.status_code == 200
        result = resp.json()["x_policy"]
        assert result["valid"] is False

    def test_invalid_json(self):
        resp = self.client.post(self.url, json={"x_policy": "{bad json"})
        assert resp.status_code == 200
        result = resp.json()["x_policy"]
        assert result["valid"] is False
        assert any("Invalid JSON" in e for e in result["errors"])


class TestFineGrainedConfigHeader:
    """Validate X-Config header via the endpoint."""

    def setup_method(self):
        test_config = get_test_config()
        self.url = f"{test_config.base_url.rstrip('/')}{VALIDATE_HEADERS_PATH}"
        self.client = httpx.Client(timeout=30)

    def teardown_method(self):
        self.client.close()

    def _validate(self, header: FineGrainedConfigHeader) -> dict:
        resp = self.client.post(self.url, json={"x_config": header.dump_for_headers()})
        assert resp.status_code == 200
        return resp.json()["x_config"]

    def test_single_llm_default(self):
        result = self._validate(FineGrainedConfigHeader.single_llm())
        assert result["valid"] is True

    def test_dual_llm_default(self):
        result = self._validate(FineGrainedConfigHeader.dual_llm())
        assert result["valid"] is True
        assert result["normalized"]["fsm"]["max_n_turns"] == 5

    def test_dual_llm_custom_steps(self):
        header = FineGrainedConfigHeader.dual_llm(max_pllm_steps=8)
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["fsm"]["max_pllm_steps"] == 8

    def test_dual_llm_max_failed_steps(self):
        header = FineGrainedConfigHeader.dual_llm(max_pllm_failed_steps=3)
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["fsm"]["max_pllm_failed_steps"] == 3

    def test_dual_llm_disable_rllm(self):
        header = FineGrainedConfigHeader.dual_llm(disable_rllm=True)
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["fsm"]["disable_rllm"] is True

    def test_dual_llm_response_format(self):
        header = FineGrainedConfigHeader.dual_llm(
            include_program=True,
            include_policy_check_history=True,
        )
        result = self._validate(header)
        assert result["valid"] is True
        assert result["normalized"]["response_format"]["include_program"] is True
        assert result["normalized"]["response_format"]["include_policy_check_history"] is True

    def test_all_entries_set(self):
        header = FineGrainedConfigHeader(
            fsm=FsmOverrides(
                max_pllm_steps=3,
                max_pllm_failed_steps=2,
                clear_history_every_n_attempts=2,
                retry_on_policy_violation=True,
                force_to_cache=["my_tool_.*"],
                min_num_tools_for_filtering=5,
                clear_session_meta="every_attempt",
                disable_rllm=False,
                reduced_grammar_for_rllm_review=True,
                max_n_turns=3,
                enable_multistep_planning=True,
                prune_failed_steps=True,
                enabled_internal_tools=["parse_with_ai", "verify_hypothesis"],
                max_tool_calls_per_step=100,
            ),
            prompt=PromptOverrides(
                pllm=PllmPromptOverrides(
                    debug_info_level="extra",
                    clarify_ambiguous_queries=True,
                    context_var_visibility="basic-notext",
                ),
            ),
            response_format=ResponseFormatOverrides(
                strip_response_content=False,
                include_program=True,
                include_policy_check_history=True,
                include_namespace_snapshot=True,
            ),
        )
        result = self._validate(header)
        assert result["valid"] is True

    def test_extra_field_rejected(self):
        resp = self.client.post(self.url, json={"x_config": '{"fsm": {"max_n_turns": 5}, "nonexistent": true}'})
        assert resp.status_code == 200
        result = resp.json()["x_config"]
        assert result["valid"] is False

    def test_invalid_json(self):
        resp = self.client.post(self.url, json={"x_config": "}{not json"})
        assert resp.status_code == 200
        result = resp.json()["x_config"]
        assert result["valid"] is False
        assert any("Invalid JSON" in e for e in result["errors"])


class TestCombinedHeaders:
    """Validate multiple headers in a single request."""

    def setup_method(self):
        test_config = get_test_config()
        self.url = f"{test_config.base_url.rstrip('/')}{VALIDATE_HEADERS_PATH}"
        self.client = httpx.Client(timeout=30)

    def teardown_method(self):
        self.client.close()

    def test_all_three_valid(self):
        features = FeaturesHeader.dual_llm(toxicity_filter=True)
        policy = SecurityPolicyHeader.dual_llm(mode="standard")
        config = FineGrainedConfigHeader.dual_llm(max_n_turns=10)
        resp = self.client.post(
            self.url,
            json={
                "x_features": features.dump_for_headers(),
                "x_policy": policy.dump_for_headers(),
                "x_config": config.dump_for_headers(),
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["x_features"]["valid"] is True
        assert body["x_policy"]["valid"] is True
        assert body["x_config"]["valid"] is True

    def test_no_headers_provided(self):
        resp = self.client.post(self.url, json={})
        assert resp.status_code == 200
        body = resp.json()
        assert body["x_features"] is None
        assert body["x_policy"] is None
        assert body["x_config"] is None

    def test_partial_valid_partial_invalid(self):
        features = FeaturesHeader.single_llm()
        resp = self.client.post(
            self.url,
            json={
                "x_features": features.dump_for_headers(),
                "x_policy": "{invalid json!",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["x_features"]["valid"] is True
        assert body["x_policy"]["valid"] is False
        assert body["x_config"] is None

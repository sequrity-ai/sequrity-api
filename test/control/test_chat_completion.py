from typing import Literal

import pytest

from sequrity_api import client
from sequrity_api.service_provider import LlmServiceProviderEnum
from sequrity_api.types.control.headers import FeaturesHeader, FineGrainedConfigHeader, SecurityPolicyHeader
from sequrity_api_unittest.config import get_test_config


class TestChatCompletion:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = client.SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url
        )

    @pytest.mark.parametrize("llm_mode", ["single-llm", "dual-llm"])
    @pytest.mark.parametrize("service_provider", ["default"] + list(LlmServiceProviderEnum))
    def test_minimal(
        self, llm_mode: Literal["single-llm", "dual-llm"], service_provider: LlmServiceProviderEnum | Literal["default"]
    ):
        if llm_mode == "single-llm":
            features_header = FeaturesHeader.create_single_llm_headers()
        else:
            features_header = FeaturesHeader.create_dual_llm_headers()

        policy_header = SecurityPolicyHeader.create_default()

        messages = [{"role": "user", "content": "What is the largest prime number below 100?"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            service_provider=service_provider,
        )

        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert "97" in response.choices[0].message.content

    @pytest.mark.parametrize("service_provider", ["default"])
    def test_dual_llm_multi_turn(self, service_provider: LlmServiceProviderEnum | Literal["default"]):
        features_header = FeaturesHeader.create_dual_llm_headers()
        policy_header = SecurityPolicyHeader.create_default()
        config_header = FineGrainedConfigHeader(max_n_turns=5)

        messages = [
            {"role": "user", "content": "Book me the flight BA263 from New York to San Francisco on 10th June, 2026."}
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "book_flight",
                    "description": "Books a flight with given flight number, origin, destination and date. Returns a booking reference number (str).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "flight_number": {"type": "string", "description": "The flight number."},
                            "origin": {"type": "string", "description": "The origin city."},
                            "destination": {"type": "string", "description": "The destination city."},
                            "date": {"type": "string", "description": "The date of the flight in YYYY-MM-DD format."},
                        },
                        "required": ["flight_number", "origin", "destination", "date"],
                    },
                },
            }
        ]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
            tools=tools,
        )
        print("First response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        # check the response is tool call
        assert response.choices[0].finish_reason == "tool_calls"
        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) > 0
        assert response.choices[0].message.tool_calls[0].function.name == "book_flight"
        assert "BA263" in response.choices[0].message.tool_calls[0].function.arguments
        assert "2026-06-10" in response.choices[0].message.tool_calls[0].function.arguments
        # append tool call msg to messages
        tool_call_msg = response.choices[0].message
        messages.append(tool_call_msg.model_dump(mode="json"))
        # Simulate tool execution and provide the result back to the model
        tool_result_msg = {
            "role": "tool",
            "content": "Flight booked successfully. Your booking reference number is ABC12345.",
            "tool_call_id": tool_call_msg.tool_calls[0].id,
        }
        messages.append(tool_result_msg)
        # Continue the conversation
        messages.append(
            {
                "role": "user",
                "content": "Thanks! Can you also book a return flight (flight number BA289) on 20th June, 2026?",
            }
        )
        response_2 = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
            tools=tools,
            session_id=response.session_id,
        )
        print("Second response:", response_2)
        # this should be another tool call for return flight
        assert response_2 is not None
        assert len(response_2.choices) > 0
        assert response_2.choices[0].message is not None
        assert response_2.choices[0].message.content is not None
        assert response_2.choices[0].finish_reason == "tool_calls"
        assert response_2.choices[0].message.tool_calls is not None
        assert len(response_2.choices[0].message.tool_calls) > 0
        assert response_2.choices[0].message.tool_calls[0].function.name == "book_flight"
        assert "BA289" in response_2.choices[0].message.tool_calls[0].function.arguments
        assert "2026-06-20" in response_2.choices[0].message.tool_calls[0].function.arguments
        # append tool call msg to messages
        tool_call_msg_2 = response_2.choices[0].message
        messages.append(tool_call_msg_2.model_dump(mode="json"))
        # Simulate tool execution and provide the result back to the model
        tool_result_msg_2 = {
            "role": "tool",
            "content": "Return flight booked successfully. Your booking reference number is XYZ67890.",
            "tool_call_id": tool_call_msg_2.tool_calls[0].id,
        }
        messages.append(tool_result_msg_2)
        # send tool result message
        response_3 = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
            tools=tools,
            session_id=response_2.session_id,
        )
        # this should be a final response from the model
        assert response_3 is not None
        assert len(response_3.choices) > 0
        assert response_3.choices[0].message is not None
        assert response_3.choices[0].message.content is not None
        print("Final response content:", response_3.choices[0].message.content)

    @pytest.mark.parametrize("service_provider", ["default"])
    def test_dual_llm_policy_enforcement(self, service_provider: LlmServiceProviderEnum | Literal["default"]):
        features_header = FeaturesHeader.create_dual_llm_headers()
        # Create a policy that forbids discussing politics
        sqrt_lite_codes = r"""
        Tag load_applicant_profile(...) -> |= {"internal_use_only", "tool/load_applicant_profile"};
        Hard Deny send_email(...) if body.tags is_superset {"internal_use_only"} & ~ (to.value in {r".*@trustedcorp\.com"});
        """
        policy_header = SecurityPolicyHeader.create_default(language="sqrt-lite", codes=sqrt_lite_codes)
        config_header = FineGrainedConfigHeader(max_n_turns=1, retry_on_policy_violation=False)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "load_applicant_profile",
                    "description": "Loads the profile of an applicant given their applicant ID. Returns the profile information as a string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "applicant_id": {
                                "type": "string",
                                "description": "The unique identifier of the applicant.",
                            },
                        },
                        "required": ["applicant_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Sends an email to the specified recipient with the given subject and body.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "The recipient's email address."},
                            "subject": {"type": "string", "description": "The subject of the email."},
                            "body": {"type": "string", "description": "The body content of the email."},
                        },
                        "required": ["to", "subject", "body"],
                    },
                },
            },
        ]

        messages = [{"role": "user", "content": "Load 'applicant-829''s profile and send it to hr@gmail.com"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
            tools=tools,
        )
        print("Response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        # check the response is tool call
        assert response.choices[0].finish_reason == "tool_calls"
        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) > 0
        assert response.choices[0].message.tool_calls[0].function.name == "load_applicant_profile"
        assert "applicant-829" in response.choices[0].message.tool_calls[0].function.arguments
        # simulate tool execution and provide the result back to the model
        tool_call_msg = response.choices[0].message
        messages.append(tool_call_msg.model_dump(mode="json"))
        tool_result_msg = {
            "role": "tool",
            "content": "Applicant Profile: Name: John Doe, Experience: 5 years in software engineering.",
            "tool_call_id": tool_call_msg.tool_calls[0].id,
        }
        messages.append(tool_result_msg)
        # continue the conversation
        response_2 = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
            tools=tools,
            session_id=response.session_id,
        )
        print("Second Response:", response_2)
        assert response_2 is not None
        assert len(response_2.choices) > 0
        assert response_2.choices[0].message is not None
        assert response_2.choices[0].message.content is not None
        # check that the model refused to send the email due to policy
        print("Second response content:", response_2.choices[0].message.content)
        assert "Tool call send_email denied by argument checking policies" in response_2.choices[0].message.content

    @pytest.mark.parametrize("service_provider", ["default"])
    def test_all_header_entries_set(self, service_provider: LlmServiceProviderEnum | Literal["default"]):
        """
        Test that all header entries can be set with non-None values.
        This validates that the header classes match the server-side parsing.
        """
        from sequrity_api.types.control.headers.feature_headers import (
            ConstraintFeature,
            LlmModeFeature,
            LongProgramSupportFeature,
            TaggerFeature,
        )
        from sequrity_api.types.control.headers.policy_headers import (
            ControlFlowMetaPolicy,
            InternalPolicyPreset,
        )
        from sequrity_api.types.control.headers.session_config_headers import ResponseFormat

        # FeaturesHeader with ALL entries set (no None values)
        # Note: file_blocker is NOT a valid feature - it doesn't exist on the server.
        # The ConstraintFeature.name field allows "file_blocker" but this is a BUG in the client.
        # See secure-orchestrator feature_registry.py - only "url_blocker" is registered.
        features_header = FeaturesHeader(
            llm=LlmModeFeature(feature_name="Dual LLM", mode="standard"),
            taggers=[
                TaggerFeature(
                    feature_name="Toxicity Filter", threshold=0.7, enabled=True, mode="normal", tag_name="toxicity"
                ),
                TaggerFeature(feature_name="PII Redaction", threshold=0.6, enabled=True, mode="strict", tag_name="pii"),
                TaggerFeature(
                    feature_name="Healthcare Topic Guardrail",
                    threshold=0.5,
                    enabled=True,
                    mode="normal",
                    tag_name="healthcare",
                ),
                TaggerFeature(
                    feature_name="Finance Topic Guardrail",
                    threshold=0.5,
                    enabled=True,
                    mode="normal",
                    tag_name="finance",
                ),
                TaggerFeature(
                    feature_name="Legal Topic Guardrail", threshold=0.5, enabled=True, mode="normal", tag_name="legal"
                ),
            ],
            constraints=[
                ConstraintFeature(feature_name="URL Blocker", name="url_blocker", enabled=True),
            ],
            long_program_support=LongProgramSupportFeature(feature_name="Long Program Support", mode="mid"),
        )

        # SecurityPolicyHeader with ALL entries set (no None values)
        policy_header = SecurityPolicyHeader(
            language="sqrt-lite",
            codes="",  # empty policy codes, just testing header parsing
            auto_gen=False,
            fail_fast=True,
            internal_policy_preset=InternalPolicyPreset(
                default_allow=True,
                enable_non_executable_memory=True,
                branching_meta_policy=ControlFlowMetaPolicy(
                    mode="deny",
                    producers=("test_producer",),
                    tags=("__non_executable", "__tool/parse_with_ai"),
                    consumers=("test_consumer",),
                ),
                enable_llm_blocked_tag=False,
            ),
        )

        # FineGrainedConfigHeader with ALL entries set (no None values)
        config_header = FineGrainedConfigHeader(
            max_pllm_attempts=3,
            merge_system_messages=True,
            convert_system_to_developer_messages=False,
            include_other_roles_in_user_query=["assistant", "tool"],
            max_tool_calls_per_attempt=100,
            clear_history_every_n_attempts=2,
            retry_on_policy_violation=True,
            cache_tool_result="all",
            force_to_cache=["my_tool_.*"],
            min_num_tools_for_filtering=5,
            clear_session_meta="every_attempt",
            disable_rllm=False,
            reduced_grammar_for_rllm_review=True,
            rllm_confidence_score_threshold=0.8,
            pllm_debug_info_level="extra",
            max_n_turns=3,
            enable_multi_step_planning=True,
            prune_failed_steps=True,
            enabled_internal_tools=["parse_with_ai", "verify_hypothesis"],
            restate_user_query_before_planning=True,
            pllm_can_ask_for_clarification=True,
            reduced_grammar_version="v2",
            response_format=ResponseFormat(
                strip_response_content=False,
                include_program=True,
                include_policy_check_history=True,
                include_namespace_snapshot=True,
            ),
            show_pllm_secure_var_values="basic-notext",
        )

        messages = [{"role": "user", "content": "What is 2 + 2?"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            service_provider=service_provider,
        )

        print("Response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        # Simple arithmetic check
        assert "4" in response.choices[0].message.content

    @pytest.mark.parametrize("service_provider", ["default"])
    def test_factory_methods_single_llm_all_features(
        self, service_provider: LlmServiceProviderEnum | Literal["default"]
    ):
        """
        Test FeaturesHeader.create_single_llm_headers with all features enabled.
        """
        features_header = FeaturesHeader.create_single_llm_headers(
            toxicity_filter=True,
            pii_redaction=True,
            healthcare_guardrail=True,
            finance_guardrail=True,
            legal_guardrail=True,
            url_blocker=True,
            long_program_mode="mid",
        )
        policy_header = SecurityPolicyHeader.create_default()

        messages = [{"role": "user", "content": "What is 3 + 3?"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            service_provider=service_provider,
        )

        print("Response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None

    @pytest.mark.parametrize("llm_mode", ["standard", "strict", "custom"])
    @pytest.mark.parametrize("service_provider", ["default"])
    def test_factory_methods_dual_llm_modes(
        self,
        llm_mode: Literal["standard", "strict", "custom"],
        service_provider: LlmServiceProviderEnum | Literal["default"],
    ):
        """
        Test FeaturesHeader.create_dual_llm_headers with different LLM modes.
        """
        features_header = FeaturesHeader.create_dual_llm_headers(
            mode=llm_mode,
            toxicity_filter=True,
            url_blocker=True,
            long_program_mode="base",
        )
        policy_header = SecurityPolicyHeader.create_default()

        messages = [{"role": "user", "content": "What is 5 + 5?"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            service_provider=service_provider,
        )

        print(f"Response for mode={llm_mode}:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None

    @pytest.mark.parametrize("language", ["sqrt", "sqrt-lite", "cedar"])
    @pytest.mark.parametrize("service_provider", ["default"])
    def test_factory_methods_security_policy_languages(
        self,
        language: Literal["sqrt", "sqrt-lite", "cedar"],
        service_provider: LlmServiceProviderEnum | Literal["default"],
    ):
        """
        Test SecurityPolicyHeader.create_default with different policy languages.
        """
        features_header = FeaturesHeader.create_dual_llm_headers()
        policy_header = SecurityPolicyHeader.create_default(
            language=language,
            codes="",
            auto_gen=False,
            fail_fast=True if language != "cedar" else None,  # fail_fast only for sqrt languages
            default_allow=True,
            enable_non_executable_memory=True,
        )

        messages = [{"role": "user", "content": "What is 7 + 7?"}]
        response = self.sequrity_client.control.create_chat_completion(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            service_provider=service_provider,
        )

        print(f"Response for language={language}:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None

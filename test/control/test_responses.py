import pytest

from sequrity import SequrityClient
from sequrity.control import FeaturesHeader, FineGrainedConfigHeader, FsmOverrides, SecurityPolicyHeader
from sequrity.types.enums import LlmServiceProvider
from sequrity_unittest.config import get_test_config


class TestResponses:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE],
    )
    def test_minimal_no_headers(self, service_provider: LlmServiceProvider):
        """Truly minimal request — no config headers at all."""
        response = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input="What is the largest prime number below 100?",
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            provider=service_provider,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        assert response is not None
        assert response.id is not None
        assert response.object == "response"
        assert response.status == "completed"
        assert len(response.output) > 0
        assert response.output_text is not None
        assert "97" in response.output_text

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE],
    )
    def test_dual_llm_multi_turn(self, service_provider: LlmServiceProvider):
        features_header = FeaturesHeader.dual_llm()
        config_header = FineGrainedConfigHeader(fsm=FsmOverrides(max_n_turns=5, enabled_internal_tools=[]))

        # First turn: ask model to book a flight
        response = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input=[
                {
                    "role": "user",
                    "content": "Book me the flight BA263 from New York to San Francisco on 10th June, 2026.",
                }
            ],
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=[
                {
                    "type": "function",
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
                }
            ],
        )
        print("First response:", response)
        assert response is not None
        assert response.status == "completed"
        assert len(response.output) > 0

        # Find the function_call in output
        from sequrity.types.responses.response import FunctionToolCall

        tool_calls = [item for item in response.output if isinstance(item, FunctionToolCall)]
        assert len(tool_calls) > 0
        assert tool_calls[0].name == "book_flight"
        assert "BA263" in tool_calls[0].arguments
        assert "2026-06-10" in tool_calls[0].arguments

        # Second turn: provide tool result and ask for return flight
        second_input = []
        # Add tool result
        second_input.append(
            {
                "type": "function_call_output",
                "call_id": tool_calls[0].call_id,
                "output": "Flight booked successfully. Your booking reference number is ABC12345.",
            }
        )
        # Add follow-up message
        second_input.append(
            {
                "role": "user",
                "content": "Thanks! Can you also book a return flight (flight number BA289) on 20th June, 2026?",
            }
        )
        response_2 = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input=second_input,
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=[
                {
                    "type": "function",
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
                }
            ],
            previous_response_id=response.id,
        )
        print("Second response:", response_2)
        assert response_2 is not None
        assert response_2.status == "completed"
        tool_calls_2 = [item for item in response_2.output if isinstance(item, FunctionToolCall)]
        assert len(tool_calls_2) > 0
        assert tool_calls_2[0].name == "book_flight"
        assert "BA289" in tool_calls_2[0].arguments
        assert "2026-06-20" in tool_calls_2[0].arguments

        # Third turn: provide tool result
        third_input = []
        third_input.append(
            {
                "type": "function_call_output",
                "call_id": tool_calls_2[0].call_id,
                "output": "Return flight booked successfully. Your booking reference number is XYZ67890.",
            }
        )
        response_3 = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input=third_input,
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            previous_response_id=response_2.id,
        )
        assert response_3 is not None
        assert response_3.status == "completed"
        assert len(response_3.output) > 0
        assert response_3.output_text is not None
        print("Third response content:", response_3.output_text)

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE],
    )
    def test_dual_llm_policy_enforcement(self, service_provider: LlmServiceProvider):
        features_header = FeaturesHeader.dual_llm()
        sqrt_codes = r"""
        tool "load_applicant_profile" -> @tags |= {"internal_use_only", "tool/load_applicant_profile"};
        tool "send_email" {
            must deny when body.tags superset of {"internal_use_only"} and (not to.value in {str matching r".*@trustedcorp\.com"});
        }
        """
        policy_header = SecurityPolicyHeader.dual_llm(codes=sqrt_codes)
        config_header = FineGrainedConfigHeader(
            fsm=FsmOverrides(max_n_turns=1, retry_on_policy_violation=False, enabled_internal_tools=[])
        )

        tools = [
            {
                "type": "function",
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
            {
                "type": "function",
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
        ]

        # First turn: ask to load profile and send to untrusted email
        response = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input=[{"role": "user", "content": "Load 'applicant-829''s profile and send it to hr@gmail.com"}],
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        print("Response:", response)
        assert response is not None
        assert response.status == "completed"
        assert len(response.output) > 0

        # Find the function_call in output — should be load_applicant_profile
        from sequrity.types.responses.response import FunctionToolCall

        tool_calls = [item for item in response.output if isinstance(item, FunctionToolCall)]
        assert len(tool_calls) > 0
        assert tool_calls[0].name == "load_applicant_profile"
        assert "applicant-829" in tool_calls[0].arguments

        # Simulate tool execution and provide result
        second_input = []
        second_input.append(
            {
                "type": "function_call_output",
                "call_id": tool_calls[0].call_id,
                "output": "Applicant Profile: Name: John Doe, Experience: 5 years in software engineering.",
            }
        )

        response_2 = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(service_provider),
            input=second_input,
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
            previous_response_id=response.id,
        )
        print("Second Response:", response_2)
        assert response_2 is not None
        assert response_2.status == "failed"
        assert len(response_2.output) > 0
        # The model should refuse to send due to policy enforcement
        assert response_2.output_text is not None
        print("Second response content:", response_2.output_text)
        assert "'send_email' is denied" in response_2.output_text

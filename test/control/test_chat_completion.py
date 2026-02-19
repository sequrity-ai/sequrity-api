import pytest

from sequrity import SequrityClient
from sequrity.control import FeaturesHeader, FineGrainedConfigHeader, FsmOverrides, SecurityPolicyHeader
from sequrity.types.enums import LlmServiceProvider
from sequrity_unittest.config import get_test_config


class TestChatCompletion:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE, LlmServiceProvider.OPENROUTER],
    )
    def test_minimal_no_headers(self, service_provider: LlmServiceProvider | None):
        """Truly minimal request — no config headers at all.

        The server uses preset defaults from the bearer token / DB lookup.
        """
        messages = [{"role": "user", "content": "What is the largest prime number below 100?"}]
        response = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            provider=service_provider,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        assert response.choices[0].message.content is not None
        assert "97" in response.choices[0].message.content

    @pytest.mark.parametrize(
        "service_provider",
        [None, LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE, LlmServiceProvider.OPENROUTER],
    )
    def test_dual_llm_multi_turn(self, service_provider: LlmServiceProvider | None):
        features_header = FeaturesHeader.dual_llm()
        config_header = FineGrainedConfigHeader(fsm=FsmOverrides(max_n_turns=5, enabled_internal_tools=[]))

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
        response = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        print("First response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        # check the response is tool call
        assert response.choices[0].finish_reason == "tool_calls"
        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) > 0
        assert response.choices[0].message.tool_calls[0].function.name == "book_flight"
        assert "BA263" in response.choices[0].message.tool_calls[0].function.arguments
        assert "2026-06-10" in response.choices[0].message.tool_calls[0].function.arguments
        # append tool call msg to messages
        tool_call_msg = response.choices[0].message
        assert tool_call_msg.tool_calls is not None
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
        response_2 = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        print("Second response:", response_2)
        # this should be another tool call for return flight
        assert response_2 is not None
        assert len(response_2.choices) > 0
        assert response_2.choices[0].message is not None
        assert response_2.choices[0].finish_reason == "tool_calls"
        assert response_2.choices[0].message.tool_calls is not None
        assert len(response_2.choices[0].message.tool_calls) > 0
        assert response_2.choices[0].message.tool_calls[0].function.name == "book_flight"
        assert "BA289" in response_2.choices[0].message.tool_calls[0].function.arguments
        assert "2026-06-20" in response_2.choices[0].message.tool_calls[0].function.arguments
        # append tool call msg to messages
        tool_call_msg_2 = response_2.choices[0].message
        assert tool_call_msg_2.tool_calls is not None
        messages.append(tool_call_msg_2.model_dump(mode="json"))
        # Simulate tool execution and provide the result back to the model
        tool_result_msg_2 = {
            "role": "tool",
            "content": "Return flight booked successfully. Your booking reference number is XYZ67890.",
            "tool_call_id": tool_call_msg_2.tool_calls[0].id,
        }
        messages.append(tool_result_msg_2)
        # send tool result message
        response_3 = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        # this should be a final response from the model
        assert response_3 is not None
        assert len(response_3.choices) > 0
        assert response_3.choices[0].message is not None
        assert response_3.choices[0].message.content is not None
        print("Final response content:", response_3.choices[0].message.content)

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE, LlmServiceProvider.OPENROUTER],
    )
    def test_dual_llm_policy_enforcement(self, service_provider: LlmServiceProvider | None):
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
        response = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        print("Response:", response)
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message is not None
        # check the response is tool call
        assert response.choices[0].finish_reason == "tool_calls"
        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) > 0
        assert response.choices[0].message.tool_calls[0].function.name == "load_applicant_profile"
        assert "applicant-829" in response.choices[0].message.tool_calls[0].function.arguments
        # simulate tool execution and provide the result back to the model
        tool_call_msg = response.choices[0].message
        assert tool_call_msg.tool_calls is not None
        messages.append(tool_call_msg.model_dump(mode="json"))
        tool_result_msg = {
            "role": "tool",
            "content": "Applicant Profile: Name: John Doe, Experience: 5 years in software engineering.",
            "tool_call_id": tool_call_msg.tool_calls[0].id,
        }
        messages.append(tool_result_msg)
        # continue the conversation
        response_2 = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            features=features_header,
            security_policy=policy_header,
            fine_grained_config=config_header,
            provider=service_provider,
            tools=tools,
        )
        print("Second Response:", response_2)
        assert response_2 is not None
        assert len(response_2.choices) > 0
        assert response_2.choices[0].message is not None
        assert response_2.choices[0].message.content is not None
        # check that the model refused to send the email due to policy
        print("Second response content:", response_2.choices[0].message.content)
        assert "'send_email' is denied" in response_2.choices[0].message.content

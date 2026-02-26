import pytest

from sequrity import SequrityClient
from sequrity.control import FineGrainedConfigHeader, FsmOverrides
from sequrity.types.chat_completion.stream import ChatCompletionChunk
from sequrity.types.enums import LlmServiceProvider
from sequrity.types.messages.stream import (
    RawContentBlockDeltaEvent,
    RawContentBlockStartEvent,
    RawMessageDeltaEvent,
    RawMessageStartEvent,
    RawMessageStopEvent,
)
from sequrity.types.responses.stream import ResponseCompletedEvent, ResponseCreatedEvent, ResponseTextDeltaEvent
from sequrity_unittest.config import get_test_config


class TestChatCompletionStreaming:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI, LlmServiceProvider.SEQURITY_AZURE, LlmServiceProvider.OPENROUTER],
    )
    def test_chat_completion_stream(self, service_provider: LlmServiceProvider):
        """Basic streaming chat completion returns typed chunks."""
        messages = [{"role": "user", "content": "Say hello in one word."}]
        stream = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            provider=service_provider,
            stream=True,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        chunks = list(stream)
        stream.close()

        assert len(chunks) > 0
        assert all(isinstance(c, ChatCompletionChunk) for c in chunks)
        assert chunks[0].object == "chat.completion.chunk"

        # At least one chunk should have content
        content_parts = [c.choices[0].delta.content for c in chunks if c.choices and c.choices[0].delta.content]
        assert len(content_parts) > 0

        # Last chunk with choices should have a finish_reason
        chunks_with_choices = [c for c in chunks if c.choices and c.choices[0].finish_reason]
        assert len(chunks_with_choices) > 0

    @pytest.mark.parametrize(
        "service_provider",
        [LlmServiceProvider.OPENAI],
    )
    def test_chat_completion_stream_session_id(self, service_provider: LlmServiceProvider):
        """Streaming response should expose session_id."""
        messages = [{"role": "user", "content": "Hi"}]
        stream = self.sequrity_client.control.chat.create(
            messages=messages,
            model=self.test_config.get_model_name(service_provider),
            llm_api_key=self.test_config.get_llm_api_key(service_provider),
            provider=service_provider,
            stream=True,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        # Consume stream
        for _ in stream:
            pass
        stream.close()

        assert stream.session_id is not None


class TestMessagesStreaming:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    def test_messages_stream(self):
        """Basic streaming Anthropic Messages returns typed events."""
        stream = self.sequrity_client.control.messages.create(
            messages=[{"role": "user", "content": "Say hello in one word."}],
            model=self.test_config.get_model_name(LlmServiceProvider.ANTHROPIC),
            max_tokens=100,
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.ANTHROPIC),
            provider=LlmServiceProvider.ANTHROPIC,
            stream=True,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        events = list(stream)
        stream.close()

        assert len(events) > 0

        # Should start with message_start
        assert isinstance(events[0], RawMessageStartEvent)

        # Should contain content block events
        content_starts = [e for e in events if isinstance(e, RawContentBlockStartEvent)]
        assert len(content_starts) > 0

        content_deltas = [e for e in events if isinstance(e, RawContentBlockDeltaEvent)]
        assert len(content_deltas) > 0

        # Should end with message_delta and message_stop
        message_deltas = [e for e in events if isinstance(e, RawMessageDeltaEvent)]
        assert len(message_deltas) > 0

        assert isinstance(events[-1], RawMessageStopEvent)


class TestResponsesStreaming:
    def setup_method(self):
        self.test_config = get_test_config()
        self.sequrity_client = SequrityClient(
            api_key=self.test_config.api_key, base_url=self.test_config.base_url, timeout=300
        )

    def test_responses_stream(self):
        """Basic streaming OpenAI Responses API returns typed events."""
        stream = self.sequrity_client.control.responses.create(
            model=self.test_config.get_model_name(LlmServiceProvider.OPENAI),
            input="Say hello in one word.",
            llm_api_key=self.test_config.get_llm_api_key(LlmServiceProvider.OPENAI),
            provider=LlmServiceProvider.OPENAI,
            stream=True,
            fine_grained_config=FineGrainedConfigHeader(fsm=FsmOverrides(enabled_internal_tools=[])),
        )

        events = list(stream)
        stream.close()

        assert len(events) > 0

        # Should contain response lifecycle events
        created_events = [e for e in events if isinstance(e, ResponseCreatedEvent)]
        assert len(created_events) > 0

        # Should contain text delta events
        text_deltas = [e for e in events if isinstance(e, ResponseTextDeltaEvent)]
        assert len(text_deltas) > 0

        # Should end with response.completed
        completed_events = [e for e in events if isinstance(e, ResponseCompletedEvent)]
        assert len(completed_events) > 0

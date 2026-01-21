from enum import StrEnum


class SequrityProductEnum(StrEnum):
    CONTROL = "control"


SEQURITY_API_URL = "https://api.sequrity.ai"

CONTROL_API_PATHS = {
    "chat_completions": {
        "default": "/control/v1/chat/completions",
        "with_service_provider": "/control/{service_provider}/v1/chat/completions",
    },
    "responses": {
        "default": "/control/v1/responses",
    },
    "generate_policy": {
        "default": "/control/v1/generate_policy",
    },
    "vscode_chat_completions": {
        "default": "/control/vscode/{service_provider}/v1/chat/completions",
    },
    "lang_graph_chat_completions": {
        "default": "/control/lang-graph/{service_provider}/v1/chat/completions",
    },
}

---
hide:
  - navigation
---

# Release Notes

## v0.4.1

`time: 2026-02-25`

| Product  | Version |
| ---------|---------|
| Control API | `094afd3174b700f104cab612d32e3f54ad1b152c` |

??? info "v0.4.1 Release Notes"

    **New Features**

    - **Responses API**: Added OpenAI-compatible Responses API support (`/control/{endpoint_type}/v1/responses`)
      - Full request/response support with function tools, file search, web search, code interpreter, computer use, MCP, and custom tools
      - Streaming via server-sent events with lifecycle, structure, content, and reasoning events
      - Available for `chat`, `code`, and `sequrity_azure` providers
    - **Streaming Support**: Added streaming across all three main APIs (Chat Completions, Messages, Responses)
      - New `SyncStream` and `AsyncStream` wrapper classes for SSE handling in the Python client
      - Session ID tracking through streaming responses
    - **Custom Headers Documentation**: New tutorial and reference documentation for typed Pydantic header classes (`FeaturesHeader`, `SecurityPolicyHeader`, `FineGrainedConfigHeader`)

    **Configuration Enhancements**

    - Added `tool_result_transform` FSM override (`"none"` or `"codex"`) for stripping Codex CLI metadata
    - Added `history_mismatch_policy` FSM override (`"reject"`, `"restart_turn"`, `"continue"`) for handling message history divergence in stateless mode (dual-LLM only)
    - Added `stream_thoughts` response format override for streaming model thinking process

    **Improvements**

    - Request/response classes now ignore extra fields for forward compatibility
    - Enhanced type hints across LangGraph integration and headers


## v0.4

`time: 2026-02-18`

| Product  | Version |
| ---------|---------|
| Control API | `e8a5b7dd08b12560ff5a5d068e1b69aedafb710b` |


## v0.3

`time: 2026-02-04`

| Product  | Version |
| ---------|---------|
| Control API | `17620f2abd4646171fc8a462bad3fafbd2b0126b` |

??? info "v0.3 Release Notes"

    **New Features**

    - **OpenAI Agents SDK Integration**: Added `SequrityAsyncOpenAI` client for seamless integration with OpenAI Agent ADK
      - Drop-in AsyncOpenAI replacement with automatic session management
      - Full support for Sequrity security features (dual-LLM, policies, fine-grained config)
      - Comprehensive documentation and examples
    - **LangGraph Integration**
    - **Type Checking**: Integrated `ty` type checker into CI/CD pipeline
      - All source code now type-checked with `ty`
      - Added to `just lint` command for local development
    - **CI Improvements**:
      - Added GitHub Actions CI workflow with linting and type checking
      - Configured test environment with required API keys
      - Added `pytest-asyncio` for async test support

    **Dependencies**

    - Added `openai>=1.0.0` to core dependencies for async client support
    - Added `ty` to dev dependencies for type checking
    - Added `pytest-asyncio>=0.24.0` to dev dependencies
    - Added optional `agents` dependency group for OpenAI Agent ADK support

    **Documentation**

    - Added integration documentation for OpenAI Agent ADK
    - Updated navigation to include Integrations reference
    - Improved code examples (removed doctest prompts, added proper code blocks)

## v0.0.2

`time: 2026-01-28`

| Product  | Version |
| ---------|---------|
| Control API | `17620f2abd4646171fc8a462bad3fafbd2b0126b` |

- Change default value of `clarify_ambiguous_queries` in `X-Config` header (`prompt.pllm.clarify_ambiguous_queries`) to `true`.
- Update docs deployment workflow to set default to `dev` instead of `latest` until docs are stable.

## v0.0.1

`time: 2026-01-27`

| Product  | Version |
| ---------|---------|
| Control API | `7f38fd23c5eea17f5efdcc387b4f5f1ef58c8333` |

- Initial release of Sequrity API documentation.
- Sequrity Control reference for REST API and Python client, getting started guides, and examples.
---
hide:
  - navigation
---

# Release Notes


## v0.0.3

`time: 2026-02-04`

| Product  | Version |
| ---------|---------|
| Control API | `17620f2abd4646171fc8a462bad3fafbd2b0126b` |

### New Features

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

### Dependencies

- Added `openai>=1.0.0` to core dependencies for async client support
- Added `ty` to dev dependencies for type checking
- Added `pytest-asyncio>=0.24.0` to dev dependencies
- Added optional `agents` dependency group for OpenAI Agent ADK support

### Documentation

- Added integration documentation for OpenAI Agent ADK
- Updated navigation to include Integrations reference
- Improved code examples (removed doctest prompts, added proper code blocks)

## v0.0.2

`time: 2026-01-28`

| Product  | Version |
| ---------|---------|
| Control API | `17620f2abd4646171fc8a462bad3fafbd2b0126b` |

- Change default value of `pllm_can_ask_for_clarification` in `security_config` header to `true`.
- Update docs deployment workflow to set default to `dev` instead of `latest` until docs are stable.

## v0.0.1

`time: 2026-01-27`

| Product  | Version |
| ---------|---------|
| Control API | `7f38fd23c5eea17f5efdcc387b4f5f1ef58c8333` |

- Initial release of Sequrity API documentation.
- Sequrity Control reference for REST API and Python client, getting started guides, and examples.
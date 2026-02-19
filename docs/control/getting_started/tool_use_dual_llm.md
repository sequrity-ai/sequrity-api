# Secure Tool Use with Dual-LLM

As mentioned at the end of [Sending your first message](./first_message.md), [Dual-LLM](../learn/single-vs-dual-llm.md#dual-llm-agent-the-camel-framework) enables advanced security features when tool calls are involved.
This tutorial demonstrates how to use Sequrity's Dual-LLM feature to secure tool calling in chat completion workflows.
Specifically, the example below illustrate
how to enforce security policies that prevent sensitive data from being sent to unauthorized recipients.

## Prerequisites

Before starting, ensure you have the following API keys:

- **Sequrity API Key**: Sign up at [Sequrity.ai](https://sequrity.ai) to get your API key from the dashboard
- **LLM Provider API Key**: You can consider Sequrity as a relay service that forwards your requests to LLM service providers, thus you need to offer LLM API keys which Sequrity Control will use for the planning LLM (PLLM) and quarantined LLM (QLLM). This example uses OpenRouter, but you can use any *supported provider*[^1].

[^1]: See [Supported Providers](../../general/rest_api/service_provider.md) for a list of supported LLM providers in REST API, and [LLM Service Provider Enum](../../general/sequrity_client/service_provider.md) for Sequrity Client.

Set these keys as environment variables:

```bash
export SEQURITY_API_KEY="your-sequrity-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

??? tip "Download Tutorial Scripts"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/tool_use_dual_llm/sequrity_client.py)
    - [REST API version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/tool_use_dual_llm/rest_api.py)

## Installation

Install the required packages based on your preferred approach:

=== "Sequrity Client"

    ```bash
    pip install sequrity rich
    ```

=== "REST API"
    For ease of reading, we use `requests` library to demonstrate the REST API calls.
    ```bash
    pip install requests rich
    ```

The `rich` package is optional but provides nice formatted output for demonstrations.

## Tool Use in Chat Completion

Tool use (also known as function calling) allows LLMs to interact with external APIs and services. In a typical tool use flow:

1. A user sends a message requesting some action that requires tool use, and offers tool definitions like input schema and descriptions to the LLM.

2. The LLM returns an **assistant message** with `tool_calls` containing the function name and arguments.

    ??? info "Example Assistant Message with Tool Call"
        ```python
        {
            "content": "",
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tc-6e0ec4e8-f7ef-11f0-8bfb-9166...",
                    "function": {
                        "arguments": '{"doc_id": "DOC12345"}',
                        "name": "get_internal_document",
                    },
                    "type": "function",
                }
            ],
        }
        ```

3. Your application executes the tool and returns a **tool message** with the result.

    ??? info "Example Tool Message with Tool Result"
        ```python
        {
            "role": "tool",
            "content": "The document content is: 'Sequrity is a secure AI...'",
            "tool_call_id": "tc-6e0ec4e8-f7ef-11f0-8bfb-9166...",
        }
        ```

4. Append the tool call and tool result messages to the conversation history, then send it back to the LLM for further processing.

For a comprehensive guide on tool use, see [OpenAI's function calling tutorial](https://developers.openai.com/cookbook/examples/how_to_call_functions_with_chat_models).

## Security Features, Policies, and Fine-Grained Configs

Sequrity Control provides powerful and fine-grained control over tool use through custom headers. Let's examine the security configuration used in this example:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:imports"
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:security_headers"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:imports"
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:security_headers"
    ```

- **`X-Features`**: Enables the Dual-LLM feature in this example
- **`X-Policy`**: Defines security policies in [SQRT language](../reference/sqrt/index.md):

    ```rust
    // Define sensitive document tags
    let sensitive_docs = {"internal_use", "confidential"};
    // Add tags to tool results of get_internal_document
    tool "get_internal_document" -> @tags |= sensitive_docs;
    // Hard deny sending emails if body contains sensitive tags
    // and recipient does not match trusted pattern
    tool "send_email" {
        hard deny when (body.tags overlaps sensitive_docs) and
        (not to.value in {str matching r".*@trustedcorp\.com"});
    }
    ```

    The policies do the following:

    - Tags documents retrieved by `get_internal_document` as `internal_use` and `confidential`
    - Blocks `send_email` calls if the email body contains sensitive tags AND the recipient is not from `trustedcorp.com`

- **`X-Config`**: Controls response format - `include_program: true` returns the generated execution program for auditing and transparency

## Tool Definitions

Both examples use two tools: one for retrieving internal documents and another for sending emails.

```python
def get_internal_document(doc_id: str) -> str:
    ...

def send_email(to: str, subject: str, body: str) -> str:
    ...
```

Here we follow [the OpenAI chat completion's tool definition format](https://platform.openai.com/docs/api-reference/chat/create#chat_create-tools) to define these tools:

??? info "Tool Definitions of `get_internal_document` and `send_email`"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:tool_defs"
    ```

## Case 1: Blocking Emails to Untrusted Domains

Now we demonstrate how Sequrity blocks attempts to send sensitive documents to an untrusted email address `research@gmail.com`.

### Step 1: Setup Client & Model

Sequrity Control API allows you to specify two LLMs for Dual-LLM tool use:
PLLM for generating the execution plan, and QLLM for processing data.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:imports"
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:client_setup"
    ```

=== "REST API"
    We define a helper function `chat_completion` to call the chat completion endpoint.
    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:imports"
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:client_setup"

    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:chat_completion_func"

    ```

### Step 2: Send User Query

The user requests to retrieve an internal document and email it to an untrusted domain (`research@gmail.com`).
Note that we need to keep track of the `session_id` to maintain context across multiple tool calls.

=== "Sequrity Client"
    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:untrusted_query"
    ```

=== "REST API"
    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:untrusted_query"
    ```

### Step 3: LLM Calls get_internal_document

The LLM first calls `get_internal_document` to retrieve the document. This tool call is allowed because there are no denying policies for it[^2].

[^2]: `get_internal_documet` has no user-defined policy but got allowed. This is because [`InternalPolicyPresets`](../reference/sequrity_client/headers/policy_header.md#sequrity.control.types.headers.InternalPolicyPresets) has `default_allow=true` by default.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:tool_call_check"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:tool_call_check"
    ```

### Step 4: Return Tool Result

Simulate the tool execution and return the sensitive document content.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:tool_result"
    ```
=== "REST API"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:tool_result"
    ```

### Step 5: Security Policy Blocks send_email

When the LLM attempts to call `send_email`, Sequrity detects that the email body contains sensitive tags and the recipient is not from a trusted domain. The tool call is blocked.

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:denied_response"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:denied_response"
    ```

### Expected Output

You may see a program like this generated by the PLLM:

```text hl_lines="19 20"
🚨 Send email denied by security policy
Error: Tool call send_email denied by argument checking policies.
Tool calls: {...}. Checking results: {'final_verdict': 'hard_denied', ...}

Generated Program:
   1 # Retrieve the internal document and email it
   2 final_return_value = None
   3
   4 doc_id = "DOC12345"
   5 recipient = "research@gmail.com"
   6 subject = f"Internal Document {doc_id}"
   7
   8 # Get the document content
   9 document_content = get_internal_document(doc_id=doc_id)
  10
  11 # Prepare email body
  12 email_body = f"Attached is the content of internal document {doc_id}:\n\n{document_content}"
  13
  14 # Send the email (🚨 BLOCKED HERE)
  15 send_result = send_email(to=recipient, subject=subject, body=email_body)
```

The security policy successfully blocks the email because:

1. The document returned by `get_internal_document` is tagged as `internal_use` and `confidential`
2. These two tags propagate to the email body in line 12's string formatting
3. The recipient `research@gmail.com` doesn't match the trusted pattern `.*@trustedcorp\.com`, thus violating the hard deny policy for `send_email`.

## Case 2: Allowing Emails to Trusted Domains

Now let's see what happens when emailing to a trusted domain.

### Send Query with Trusted Recipient

Change the recipient to `user@trustedcorp.com` and start a new session:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:trusted_query"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:trusted_query"
    ```

### Execute Tool Calls

Following the same flow as before:

1. LLM calls `get_internal_document` - return the document content
2. LLM calls `send_email` - **this time it's allowed!**
3. Return `send_email` result
4. Get final response from LLM

??? info "Tool Call Executions with Trusted Recipient"
    === "Sequrity Client"

        ```python
        --8<-- "examples/control/getting_started/tool_use_dual_llm/sequrity_client.py:trusted_flow"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/getting_started/tool_use_dual_llm/rest_api.py:trusted_flow"
        ```

### Expected Output

```text hl_lines="3-5 21-26"
✅ Email allowed to trusted domain
Status: success
Return Value: {'value': {'status': 'success', 'doc_id': 'DOC12345',
'emailed_to': 'user@trustedcorp.com',
'message': 'Document retrieved and emailed successfully.'}, ...}

Generated Program:
   1 # Retrieve the document and email it to the recipient.
   2 final_return_value = None
   3
   4 try:
   5     doc_content = get_internal_document(doc_id="DOC12345")
   6     email_subject = "Requested document DOC12345"
   7     email_body = (
   8         "Hello,\n\n"
   9         "Attached below is the content of internal document DOC12345 as requested:\n\n"
  10         f"{doc_content}\n\n"
  11         "Regards,\nAutomated Document Service"
  12     )
  13     send_email(to="user@trustedcorp.com", subject=email_subject, body=email_body)
  14     final_return_value = {
  15         "status": "success",
  16         "doc_id": "DOC12345",
  17         "emailed_to": "user@trustedcorp.com",
  18         "message": "Document retrieved and emailed successfully."
  19     }
  20 except Exception as e:
  21     final_return_value = {"status": "error", "error": str(e)}
```

This time the email is allowed because the recipient matches the trusted domain pattern `.*@trustedcorp\.com`, even though the email body contains sensitive tags.

## Key Takeaways

1. Dual-LLM separate control flow and data processing, where the control flow is a python program generated by the PLLM.
2. MetaData like tags propagate through the program execution
3. Sequrity Control API enforces security policies on tool calls based on the propagated metadata, preventing unauthorized actions


## More Complex Examples

Sequrity Control API supports more complex scenarios, such as enforcing complex business logics, ensuring factuality with data provenance, enforcing legal and compliance mandates, fairness, and interpretability. Go and explore [more examples](../examples/index.md) to see how Sequrity can help secure your LLM applications!

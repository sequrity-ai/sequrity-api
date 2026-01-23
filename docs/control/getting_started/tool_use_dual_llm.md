# Secure Tool Use with Dual-LLM

As mentioned at the end of [Sending your first message](./first_message.md), Dual-LLM enables advanced security features when tool calls are involved.
This tutorial demonstrates how to use Sequrity's Dual-LLM feature to secure tool calling in chat completion workflows.
Specifically, the two examples below illustrate
how to enforce security policies that prevent sensitive data from being sent to unauthorized recipients.

## Prerequisites

Before starting, ensure you have the following API keys:

- **Sequrity API Key**: Sign up at [Sequrity](https://sequrity.ai) to get your API key from the dashboard
- **LLM Provider API Key**: This example uses OpenRouter, but you can use any supported provider

Set these keys as environment variables:

```bash
export SEQURITY_API_KEY="your-sequrity-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

??? example "Download Tutorial Scripts"

    - [Sequrity Client version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/tool_use_dual_llm/sequrity_client.py)
    - [REST API version](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/getting_started/tool_use_dual_llm/rest_api.py)

## Installation

Install the required packages based on your preferred approach:

=== "Sequrity Client"

    ```bash
    pip install sequrity-api rich
    ```

=== "REST API"

    ```bash
    pip install requests rich
    ```

The `rich` package is optional but provides nice formatted output for demonstrations.

## Tool Use in Chat Completion

Tool use (also known as function calling) allows LLMs to interact with external APIs and services. In a typical tool use flow:

1. The LLM returns an **assistant message** with `tool_calls` containing the function name and arguments. Here's an example:
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
2. Your application executes the tool and returns a **tool message** with the result. Here's an example:
    ```python
    {
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI...'",
        "tool_call_id": "tc-6e0ec4e8-f7ef-11f0-8bfb-9166...",
    }
    ```
3. Append the tool call and tool result messages to the conversation history, then send it back to the LLM for further processing.

For a comprehensive guide on tool use, see [OpenAI's function calling tutorial](https://developers.openai.com/cookbook/examples/how_to_call_functions_with_chat_models).

## Security Features, Policies, and Fine-Grained Configs

Sequrity Control API provides powerful and fine-grained control over tool use through custom headers. Let's examine the security configuration used in this example:

=== "Sequrity Client"

    ```python
    from sequrity_api.types.control.headers import (
        FeaturesHeader,
        FineGrainedConfigHeader,
        SecurityPolicyHeader,
    )

    # Enable Dual-LLM mode for enhanced security
    features = FeaturesHeader.create_dual_llm_headers(mode="standard")

    # Define security policy in SQRT-Lite language
    security_policy = SecurityPolicyHeader(
        language="sqrt-lite",
        codes=r"""
        sensitive_docs = {"internal_use", "confidential"};
        Tag get_internal_document(...) -> |= sensitive_docs;
        Hard Deny send_email(...) if body.tags is_overlapping sensitive_docs
            & (~ to.value in {r".*@trustedcorp\.com"});
        """,
    )

    # Request to include generated program in response
    fine_grained_config = FineGrainedConfigHeader(
        response_format=ResponseFormat(include_program=True)
    )
    ```

=== "REST API"

    ```python
    import json

    # Enable Dual-LLM mode for enhanced security
    features = json.dumps([
        {"feature_name": "Dual LLM", "config_json": json.dumps({"mode": "standard"})},
        {"feature_name": "Long Program Support", "config_json": json.dumps({"mode": "base"})},
    ])

    # Define security policy in SQRT-Lite language
    security_policy = json.dumps({
        "language": "sqrt-lite",
        "codes": r"""
        sensitive_docs = {"internal_use", "confidential"};
        Tag get_internal_document(...) -> |= sensitive_docs;
        Hard Deny send_email(...) if body.tags is_overlapping sensitive_docs
            & (~ to.value in {r".*@trustedcorp\.com"});
        """,
    })

    # Request to include generated program in response
    fine_grained_config = json.dumps({"response_format": {"include_program": True}})
    ```

- **`X-Security-Features`**: Enables the Dual-LLM feature in this example
- **`X-Security-Policy`**: Defines security policies in [SQRT-Lite language](../reference/security_policies/index.md):
    ```c++
    // Define sensitive document tags
    sensitive_docs = {"internal_use", "confidential"};
    // Add tags to tool results of get_internal_document
    Tag get_internal_document(...) -> |= sensitive_docs;
    // Hard deny sending emails if body contains sensitive tags and recipient does not match trusted pattern
    Hard Deny send_email(...) if body.tags is_overlapping sensitive_docs
    & (~ to.value in {r".*@trustedcorp\.com"});
    ```
    - Tags documents retrieved by `get_internal_document` as `internal_use` and `confidential`
    - Blocks `send_email` calls if the email body contains sensitive tags AND the recipient is not from `trustedcorp.com`
- **`X-Security-Config`**: Controls response format - `include_program: true` returns the generated execution program for auditing and transparency

## Tool Definitions

Both examples use two tools: one for retrieving internal documents and another for sending emails. Here we simply define their interfaces for the LLM to call.

The tool definitions follow [the OpenAI chat completion's tool definition format](https://platform.openai.com/docs/api-reference/chat/create#chat_create-tools).

??? example "Tool Definitions of `get_internal_document` and `send_email`"

    === "Sequrity Client"

        ```python
        tool_defs = [
            {
                "type": "function",
                "function": {
                    "name": "get_internal_document",
                    "description": "Retrieve an internal document by its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "doc_id": {"type": "string", "description": "The ID of the internal document."}
                        },
                        "required": ["doc_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to a specified recipient.",
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
        ```

    === "REST API"

        ```python
        tool_defs = [
            {
                "type": "function",
                "function": {
                    "name": "get_internal_document",
                    "description": "Retrieve an internal document by its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "doc_id": {"type": "string", "description": "The ID of the internal document."}
                        },
                        "required": ["doc_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to a specified recipient.",
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
        ```

## Example 1: Blocking Emails to Untrusted Domains

Now we demonstrate how Sequrity blocks attempts to send sensitive documents to an untrusted email address `research@gmail.com`.

### Step 1: Setup Client & Model

Sequrity Control API allows you to specify two LLMs for Dual-LLM tool use:
PLLM (Planning LLM) for generating the execution plan, and QLLM (Query/Quarantined LLM) for processing data.

=== "Sequrity Client"

    ```python
    from sequrity_api import SequrityClient

    client = SequrityClient(api_key=sequrity_api_key)
    model = "openai/gpt-5-mini,openai/gpt-5-nano"  # PLLM, QLLM
    ```

=== "REST API"

    ```python
    import requests

    base_url = "https://api.sequrity.ai"
    model = "openai/gpt-5-mini,openai/gpt-5-nano"  # PLLM, QLLM
    ```

### Step 2: Send User Query

The user requests to retrieve an internal document and email it to an untrusted domain (`research@gmail.com`).
Note that we need to keep track of the `session_id` to maintain context across multiple tool calls.

=== "Sequrity Client"

    ```python
    user_query = "Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com"
    messages = [{"role": "user", "content": user_query}]

    response = client.control.create_chat_completion(
        messages=messages,
        model=model,
        tools=tool_defs,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
        service_provider="openrouter",
    )
    session_id = response.session_id
    ```

=== "REST API"

    ```python
    user_query = "Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com"
    messages = [{"role": "user", "content": user_query}]

    url = f"{base_url}/control/openrouter/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sequrity_api_key}",
        "X-Api-Key": openrouter_api_key,
        "X-Security-Features": features,
        "X-Security-Policy": security_policy,
        "X-Security-Config": fine_grained_config,
    }

    payload = {"messages": messages, "model": model, "tools": tool_defs}
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    session_id = response.headers.get("X-Session-Id")
    ```

### Step 3: LLM Calls get_internal_document

The LLM first calls `get_internal_document` to retrieve the document. This tool call is allowed because there are no denying policies for it[^1].

[^1]: `get_internal_documet` has no user-defined policy but got allowed. This is because [`InternalPolicyPreset`](../reference/sequrity_client/headers.md#sequrity_api.types.control.headers.policy_headers.InternalPolicyPreset) has `default_allow=true` by default.

=== "Sequrity Client"

    ```python
    tool_call = response.choices[0].message.tool_calls[0]
    assert tool_call.function.name == "get_internal_document"

    # Append assistant message with tool call
    messages.append(response.choices[0].message.model_dump(mode="json"))
    ```

=== "REST API"

    ```python
    tool_call = response_data["choices"][0]["message"]["tool_calls"][0]
    assert tool_call["function"]["name"] == "get_internal_document"

    # Append assistant message with tool call
    messages.append(response_data["choices"][0]["message"])
    ```

### Step 4: Return Tool Result

Simulate the tool execution and return the sensitive document content.

```python
messages.append({
    "role": "tool",
    "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
    "tool_call_id": tool_call.id,  # or tool_call["id"] for REST API
})
```

### Step 5: Security Policy Blocks send_email

When the LLM attempts to call `send_email`, Sequrity detects that the email body contains sensitive tags and the recipient is not from a trusted domain. The tool call is blocked.

=== "Sequrity Client"

    ```python
    response = client.control.create_chat_completion(
        messages=messages,
        model=model,
        tools=tool_defs,
        service_provider="openrouter",
        session_id=session_id,
    )

    # Parse the error response
    content = ResponseContentJsonSchema.parse_raw(response.choices[0].message.content)
    print(f"Error: {content.error.message}")
    print(f"Generated Program:\n{content.program}")
    ```

=== "REST API"

    ```python
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    # Parse the error response
    content = json.loads(response_data["choices"][0]["message"]["content"])
    print(f"Error: {content['error']['message']}")
    print(f"Generated Program:\n{content['program']}")
    ```

### Expected Output

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
2. These tags propagate to the email body in line 12
3. The recipient `research@gmail.com` doesn't match the trusted pattern `.*@trustedcorp\.com`

## Example 2: Allowing Emails to Trusted Domains

Now let's see what happens when emailing to a trusted domain.

### Send Query with Trusted Recipient

Change the recipient to `user@trustedcorp.com` and start a new session:

=== "Sequrity Client"

    ```python
    user_query = "Retrieve the internal document with ID 'DOC12345' and email it to user@trustedcorp.com"
    messages = [{"role": "user", "content": user_query}]

    response = client.control.create_chat_completion(
        messages=messages,
        model=model,
        tools=tool_defs,
        features=features,
        security_policy=security_policy,
        fine_grained_config=fine_grained_config,
        service_provider="openrouter",
    )
    session_id = response.session_id
    ```

=== "REST API"

    ```python
    user_query = "Retrieve the internal document with ID 'DOC12345' and email it to user@trustedcorp.com"
    messages = [{"role": "user", "content": user_query}]

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    session_id = response.headers.get("X-Session-Id")
    ```

### Execute Tool Calls

Following the same flow as before:

1. LLM calls `get_internal_document` - return the document content
2. LLM calls `send_email` - **this time it's allowed!**
3. Return success message from the email tool

=== "Sequrity Client"

    ```python
    # After get_internal_document call
    messages.append(response.choices[0].message.model_dump(mode="json"))
    messages.append({
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call.id,
    })

    # Get send_email tool call
    response = client.control.create_chat_completion(
        messages=messages, model=model, tools=tool_defs,
        service_provider="openrouter", session_id=session_id,
    )

    # Execute send_email
    tool_call = response.choices[0].message.tool_calls[0]
    messages.append(response.choices[0].message.model_dump(mode="json"))
    messages.append({
        "role": "tool",
        "content": "Email sent successfully",
        "tool_call_id": tool_call.id,
    })

    # Get final response
    response = client.control.create_chat_completion(
        messages=messages, model=model, tools=tool_defs,
        service_provider="openrouter", session_id=session_id,
    )

    content = ResponseContentJsonSchema.parse_raw(response.choices[0].message.content)
    ```

=== "REST API"

    ```python
    # After get_internal_document call
    messages.append(response_data["choices"][0]["message"])
    messages.append({
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call["id"],
    })

    # Get send_email tool call
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()

    # Execute send_email
    tool_call = response_data["choices"][0]["message"]["tool_calls"][0]
    messages.append(response_data["choices"][0]["message"])
    messages.append({
        "role": "tool",
        "content": "Email sent successfully",
        "tool_call_id": tool_call["id"],
    })

    # Get final response
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    content = json.loads(response_data["choices"][0]["message"]["content"])
    ```

### Expected Output

```text hl_lines="3 4 5 21 22 23 24 25 26"
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

1. In Dual-LLM, control flow and data processing are separated, enhancing security
2. Sequrity Control API enforces security policies on tool calls, preventing unauthorized actions
3. MetaData like tags propagate through program execution
4. A session ID is needed for Sequrity to track context across multiple tool calls


## More Complex Examples

Sequrity Control API supports more complex scenarios, such as enforcing complex bussiness logics, ensuring factuality with data provenance, enforcing legal and compliance mandates, fairness, and interpretability. Go and explore [more examples](../examples/index.md) to see how Sequrity can help secure your LLM applications!
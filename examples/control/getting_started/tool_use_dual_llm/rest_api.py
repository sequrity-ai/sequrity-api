# --8<-- [start:imports]
import json
import os
import re

import requests

# --8<-- [end:imports]

# Try to import rich, fallback to plain print if not available
try:
    from rich import print as rprint
    from rich.syntax import Syntax
except ImportError:

    def rprint(text=""):
        cleaned = re.sub(r"\[/?[^\]]+\]", "", str(text))
        print(cleaned)

    class Syntax:
        def __init__(self, code, lexer="", theme="", line_numbers=False, word_wrap=False):
            self.code = code

        def __repr__(self):
            return self.code


openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
sequrity_api_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
base_url = os.getenv("SEQURITY_BASE_URL", None)

assert openrouter_api_key != "your-openrouter-api-key", "Please set your OPENROUTER_API_KEY environment variable."
assert sequrity_api_key != "your-sequrity-api-key", "Please set your SEQURITY_API_KEY environment variable."

# --8<-- [start:client_setup]
service_provider = "openrouter"
model = "openai/gpt-5-mini,openai/gpt-5-nano"  # Dual-LLM: PLLM, QLLM
# --8<-- [end:client_setup]

# --8<-- [start:tool_defs]
tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "get_internal_document",
            "description": "Retrieve an internal document by its ID. Returns the document content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The ID of the internal document to retrieve.",
                    }
                },
                "required": ["doc_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a specified recipient. Returns a confirmation string upon success.",
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
# --8<-- [end:tool_defs]

# --8<-- [start:security_headers]
# Custom headers as JSON (no classes)
features = json.dumps(
    [
        {"feature_name": "Dual LLM", "config_json": json.dumps({"mode": "standard"})},
        {"feature_name": "Long Program Support", "config_json": json.dumps({"mode": "base"})},
    ]
)

security_policy = json.dumps(
    {
        "language": "sqrt",
        "codes": r"""
    let sensitive_docs = {"internal_use", "confidential"};
    tool "get_internal_document" -> @tags |= sensitive_docs;
    tool "send_email" {
        hard deny when (body.tags overlaps sensitive_docs) and (not to.value in {str matching r".*@trustedcorp\.com"});
    }
    """,
    }
)

fine_grained_config = json.dumps({"response_format": {"include_program": True}})
# --8<-- [end:security_headers]


# --8<-- [start:chat_completion_func]
def chat_completion(messages):
    url = f"{base_url}/control/{service_provider}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {sequrity_api_key}",
        "Content-Type": "application/json",
        "X-Api-Key": openrouter_api_key,
        "X-Security-Features": features,
        "X-Security-Policy": security_policy,
        "X-Security-Config": fine_grained_config,
    }

    payload = {"messages": messages, "model": model, "tools": tool_defs}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
# --8<-- [end:chat_completion_func]


rprint("\n[bold blue] Testing Dual-LLM Secure Tool Use Example[/bold blue]\n")
rprint("[bold red]" + "=" * 60 + "[/bold red]")
rprint("[bold red]Send Email to Untrusted Domain (Should be Denied)[/bold red]")
rprint("[bold red]" + "=" * 60 + "[/bold red]\n")

# --8<-- [start:untrusted_query]
user_query = "Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com"
messages = [{"role": "user", "content": user_query}]

response_data = chat_completion(messages)
# --8<-- [end:untrusted_query]
assert response_data["choices"][0]["message"]["role"] == "assistant"
# --8<-- [start:tool_call_check]
assert response_data["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "get_internal_document"
tool_call = response_data["choices"][0]["message"]["tool_calls"][0]
# --8<-- [end:tool_call_check]

# append assistant message (tool call to get_internal_document)
messages.append(response_data["choices"][0]["message"])
# --8<-- [start:tool_result]
# simulate tool execution and get tool response
messages.append(
    {
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call["id"],
    }
)
# --8<-- [end:tool_result]
rprint("\n[dim]→ Executing tool call: [bold]get_internal_document[/bold][/dim]")

# --8<-- [start:denied_response]
response_data = chat_completion(messages)
assert "denied by argument checking policies" in response_data["choices"][0]["message"]["content"]

content = json.loads(response_data["choices"][0]["message"]["content"])
rprint("\n[bold red]🚨 Send email denied by security policy[/bold red]")
rprint(f"[yellow]Error:[/yellow] {content['error']['message']}\n")

rprint("[bold yellow]Generated Program:[/bold yellow]")
syntax = Syntax(content["program"], "python", theme="monokai", line_numbers=True, word_wrap=False)
rprint(syntax)
# --8<-- [end:denied_response]

# Test with trusted domain
rprint("[bold green]" + "=" * 60 + "[/bold green]")
rprint("[bold green]Send Email to Trusted Domain (Should be Allowed)[/bold green]")
rprint("[bold green]" + "=" * 60 + "[/bold green]\n")

# --8<-- [start:trusted_query]
messages = [{"role": "user", "content": user_query.replace("research@gmail.com", "user@trustedcorp.com")}]

response_data = chat_completion(messages)
# --8<-- [end:trusted_query]
assert response_data["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "get_internal_document"
tool_call = response_data["choices"][0]["message"]["tool_calls"][0]

# --8<-- [start:trusted_flow]
messages.append(response_data["choices"][0]["message"])
messages.append(
    {
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call["id"],
    }
)
rprint("\n[dim]→ Executing tool call: [bold]get_internal_document[/bold][/dim]")

response_data = chat_completion(messages)
assert response_data["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "send_email"
tool_call = response_data["choices"][0]["message"]["tool_calls"][0]

messages.append(response_data["choices"][0]["message"])
messages.append({"role": "tool", "content": "Email sent successfully", "tool_call_id": tool_call["id"]})
rprint("\n[dim]→ Executing tool call: [bold]send_email[/bold][/dim]")

response_data = chat_completion(messages)
content = json.loads(response_data["choices"][0]["message"]["content"])
assert content["status"] == "success"
rprint("\n[bold green]✅ Email allowed to trusted domain[/bold green]")
# --8<-- [end:trusted_flow]
rprint(f"[green]Status:[/green] {content['status']}")
rprint(f"[green]Return Value:[/green] {content['final_return_value']}\n")

rprint("[bold yellow]Generated Program:[/bold yellow]")
syntax = Syntax(content["program"], "python", theme="monokai", line_numbers=True, word_wrap=False)

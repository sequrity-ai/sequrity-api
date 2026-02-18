import os
import re

# Try to import rich, fallback to plain print if not available
try:
    # pretty print with rich
    from rich import print as rprint
    from rich.syntax import Syntax
except ImportError:
    # Fallback implementations
    def rprint(text=""):
        # Strip rich markup tags like [bold], [/bold], etc.
        cleaned = re.sub(r"\[/?[^\]]+\]", "", str(text))
        print(cleaned)

    class Syntax:
        def __init__(self, code, lexer="", theme="", line_numbers=False, word_wrap=False):
            self.code = code

        def __repr__(self):
            return self.code


# --8<-- [start:imports]
# --8<-- [end:imports]
from sequrity import SequrityClient
from sequrity import (
    FeaturesHeader,
    FineGrainedConfigHeader,
    SecurityPolicyHeader,
)
from sequrity.types.dual_llm_response import ResponseContentJsonSchema
from sequrity.types.headers import ResponseFormatOverrides

openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
sequrity_key = os.getenv("SEQURITY_API_KEY", "your-sequrity-api-key")
base_url = os.getenv("SEQURITY_BASE_URL", None)

assert openrouter_api_key != "your-openrouter-api-key", "Please set your OPENROUTER_API_KEY environment variable."
assert sequrity_key != "your-sequrity-api-key", "Please set your SEQURITY_API_KEY environment variable."

# --8<-- [start:client_setup]
client = SequrityClient(api_key=sequrity_key, base_url=base_url)
service_provider = "openrouter"
model = "openai/gpt-5-mini,openai/gpt-5-nano"  # Dual-LLM: PLLM, QLLM
# --8<-- [end:client_setup]

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
                    "to": {
                        "type": "string",
                        "description": "The recipient's email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email.",
                    },
                    "body": {
                        "type": "string",
                        "description": "The body content of the email.",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]

# --8<-- [start:security_headers]
features = FeaturesHeader.dual_llm()
security_policy = SecurityPolicyHeader.dual_llm(
    codes=r"""
    let sensitive_docs = {"internal_use", "confidential"};
    tool "get_internal_document" -> @tags |= sensitive_docs;
    tool "send_email" {
        hard deny when (body.tags overlaps sensitive_docs) and (not to.value in {str matching r".*@trustedcorp\.com"});
    }
    """,
)
fine_grained_config = FineGrainedConfigHeader(response_format=ResponseFormatOverrides(include_program=True))
# --8<-- [end:security_headers]

rprint("\n[bold blue] Testing Dual-LLM Secure Tool Use Example[/bold blue]\n")
rprint("[bold red]" + "=" * 60 + "[/bold red]")
rprint("[bold red]Send Email to Untrusted Domain (Should be Denied)[/bold red]")
rprint("[bold red]" + "=" * 60 + "[/bold red]\n")
# --8<-- [start:untrusted_query]
user_query = "Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com"
messages = [{"role": "user", "content": user_query}]

response = client.chat.create(
    messages=messages,
    model=model,
    tools=tool_defs,
    features=features,
    security_policy=security_policy,
    fine_grained_config=fine_grained_config,
    provider=service_provider,
)
# --8<-- [end:untrusted_query]

assert response.choices[0].message is not None
assert response.choices[0].message.role == "assistant"
assert response.choices[0].message.tool_calls is not None
# --8<-- [start:tool_call_check]
assert response.choices[0].message.tool_calls[0].function.name == "get_internal_document"
tool_call = response.choices[0].message.tool_calls[0]
# --8<-- [end:tool_call_check]

# append assistant message (tool call to get_internal_document)
messages.append(response.choices[0].message.model_dump(mode="json"))

# --8<-- [start:tool_result]
# simulate tool execution and get tool response
messages.append(
    {
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call.id,
    }
)
# --8<-- [end:tool_result]
rprint("\n[dim]→ Executing tool call: [bold]get_internal_document[/bold][/dim]")

# --8<-- [start:denied_response]
response = client.chat.create(
    messages=messages,
    model=model,
    tools=tool_defs,
    provider=service_provider,
)
assert response.choices[0].message is not None
assert "denied by argument checking policies" in response.choices[0].message.content

content = ResponseContentJsonSchema.parse_raw(response.choices[0].message.content)
rprint("\n[bold red]🚨 Send email denied by security policy[/bold red]")
rprint(f"[yellow]Error:[/yellow] {content.error.message}\n")

rprint("[bold yellow]Generated Program:[/bold yellow]")
syntax = Syntax(content.program, "python", theme="monokai", line_numbers=True, word_wrap=False)
rprint(syntax)
# --8<-- [end:denied_response]

# However, if the email is to a trusted domain, it should be allowed
rprint("[bold green]" + "=" * 60 + "[/bold green]")
rprint("[bold green]Send Email to Trusted Domain (Should be Allowed)[/bold green]")
rprint("[bold green]" + "=" * 60 + "[/bold green]\n")
# --8<-- [start:trusted_query]
messages = [{"role": "user", "content": user_query.replace("research@gmail.com", "user@trustedcorp.com")}]

response = client.chat.create(
    messages=messages,
    model=model,
    tools=tool_defs,
    features=features,
    security_policy=security_policy,
    provider=service_provider,
    fine_grained_config=fine_grained_config,
)
# --8<-- [end:trusted_query]
assert response.choices[0].message is not None
assert response.choices[0].message.role == "assistant"
assert response.choices[0].message.tool_calls is not None
assert response.choices[0].message.tool_calls[0].function.name == "get_internal_document"
tool_call = response.choices[0].message.tool_calls[0]
# --8<-- [start:trusted_flow]
# append assistant message (tool call to get_internal_document)
messages.append(response.choices[0].message.model_dump(mode="json"))
# simulate tool execution and get tool response
messages.append(
    {
        "role": "tool",
        "content": "The document content is: 'Sequrity is a secure AI orchestration platform...'",
        "tool_call_id": tool_call.id,
    }
)
rprint("\n[dim]→ Executing tool call: [bold]get_internal_document[/bold][/dim]")
response = client.chat.create(
    messages=messages,
    model=model,
    tools=tool_defs,
    provider=service_provider,
)
# this should be tool call to send_email
assert response.choices[0].message is not None
assert response.choices[0].message.tool_calls is not None
assert response.choices[0].message.tool_calls[0].function.name == "send_email"
tool_call = response.choices[0].message.tool_calls[0]
# append assistant message (tool call to send_email)
messages.append(response.choices[0].message.model_dump(mode="json"))
# simulate tool execution and get tool response
messages.append(
    {
        "role": "tool",
        "content": "Email sent successfully",
        "tool_call_id": tool_call.id,
    }
)
rprint("\n[dim]→ Executing tool call: [bold]send_email[/bold][/dim]")
response = client.chat.create(
    messages=messages,
    model=model,
    tools=tool_defs,
    provider=service_provider,
)
# final response
assert response.choices[0].message is not None
content = ResponseContentJsonSchema.parse_raw(response.choices[0].message.content)
assert content.status == "success"
rprint("\n[bold green]✅ Email allowed to trusted domain[/bold green]")
# --8<-- [end:trusted_flow]
rprint(f"[green]Status:[/green] {content.status}")
rprint(f"[green]Return Value:[/green] {content.final_return_value}\n")

rprint("[bold yellow]Generated Program:[/bold yellow]")
syntax = Syntax(content.program, "python", theme="monokai", line_numbers=True, word_wrap=False)
rprint(syntax)

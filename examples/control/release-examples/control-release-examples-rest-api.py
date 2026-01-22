# %% [markdown]
#  Friends, we are very excited to announce **AI Sequrity Control** –- our first beta product to deploy DualLLM architecture for your AI instantiation with no headaches. **Sequrity Control** is not just yet another guardrail system –- it gives you much stronger guarantees and enables you to reason formally about requirements of your agent covering tool-use security policies and also even business logic.
#
#  Most standard AI setups use a single, powerful LLM to both understand your instructions and interact with your data. This is the simplest approach, but it's also the most vulnerable. This mixing of control-flow (the instructions to execute) and untrusted data is the root cause of prompt injection vulnerabilities. For instance, a malicious instruction hidden in a calendar invite could trick the AI into leaking sensitive commercial information.
#
#  At [**sequrity.ai**](https://sequrity.ai/), we believe in a fundamentally different and more secure design. Instead of patching a broken model, we have re-architected the entire process with our Dual-LLM, "Plan-Then-Execute" architecture. This approach creates a formal separation between understanding instructions and acting on data, providing architectural guarantees that other solutions simply can't match.
#
#  Here's how it works:
#
#  - The Planner LLM: This first model reads your prompt and creates a safe, step-by-step plan.
#  - The Security Checkpoint: This is our crucial innovation. This engine intercepts and analyzes the plan before any action is taken. It validates the plan against your defined policies, ensuring that malicious instructions found in your data can never become actions.
#  - Secure Execution: Only the vetted, secure steps of the plan are executed. Malicious instructions are correctly identified as data and ignored, preventing the instruction from ever crossing the boundary from data flow to control flow.
#
#  Below, we give a number of examples of where Sequrity Control shines.
#
#  **Stop Patching, Start Building on a Foundation of Certainty**
#
#  Sequrity Control offers a deterministic approach that makes the system's behavior predictable and auditable. It becomes architecturally impossible for the AI to violate your security policy. This fundamentally shifts liability from the unpredictable nature of an AI to the accountable decisions of a system user.
#
#  Our system enables you to enforce powerful, fine-grained policies. A policy isn't just about what role can use a certain tool; it's about defining specific conditions, such as allowing an action only if the user is a manager, the data is not personally identifiable information, and it's within work hours. This is the difference between a bouncer checking an ID at the door and a security guard monitoring actions inside.
#
#   **Below we provide special use-cases where you can already use Control**:
#
#

# %% [markdown]
#  ## Setup & Helper Functions

# %%
# @title Settling the keys and the endpoint
import json
import os
import re
from typing import Callable, Literal

import requests
from rich.console import Console
from rich.syntax import Syntax

# Client configuration
open_router_key = "your OpenRouter/OAI key"  # @param {type: "string"}
sequrity_api_key = "your SequrityAI key"  # @param {type: "string"}
endpoint_url = "https://api.sequrity.ai/control/openrouter/v1/chat/completions"  # @param {type: "string"}

CONFIG = {
    "open_router_api_key": os.getenv("OPENROUTER_API_KEY", open_router_key),
    "sequrity_api_key": os.getenv("SEQURITY_API_KEY", sequrity_api_key),
    "endpoint_url": os.getenv("ENDPOINT_URL", endpoint_url),
}

assert CONFIG["open_router_api_key"] != "your OpenRouter/OAI key"
assert CONFIG["sequrity_api_key"] != "your SequrityAI key"

# %% [markdown]
#  ### Mock client
#  Mock client sends user query, executes tools & sends results to endpoint if any, and prints these interactions.

# %% [markdown]
# Under the hood all that we do is we wrap around an LLM endpoint and pass extra headers.
#
# Namely,
# ```python
#    headers = {
#        "Content-Type": "application/json",
#        "Authorization": f"Bearer {CONFIG['sequrity_api_key']}",
#        "X-Api-Key": CONFIG["open_router_api_key"],
#        "X-Security-Features": json.dumps(enabled_features),
#    }
#    if session_id:
#        headers["X-Session-ID"] = session_id
#    if security_policies:
#        headers["X-Security-Policy"] = json.dumps(security_policies)
#    if security_config:
#        headers["X-Security-Config"] = json.dumps(security_config)
#
#    payload = {
#        "model": model,
#        "messages": messages,
#        "tools": tool_defs,
#        "reasoning_effort": reasoning_effort,
#    }
# ```
#
# To use it in your codebase just wrap around the current endpoint with out endpoint and pass a few more headers into it.

# %%
console = Console()


def run_workflow(
    model: str,
    query: str,
    tool_defs: list[dict],
    tool_map: dict[str, Callable],
    enabled_features: dict | None,
    security_policies: dict | None,
    security_config: dict | None,
    reasoning_effort: str = "minimal",
) -> Literal["success", "denied by policies", "unexpected error"]:
    session_id = None
    messages = [{"role": "user", "content": query}]
    turn_id = 1

    while True:
        print(f"\t--- Turn {turn_id} ---")
        print(f"\t📤 Sending request (Session ID: {session_id}):\n\t{messages}")
        response_json, session_id = send_request_to_endpoint(
            model=model,
            messages=messages,
            session_id=session_id,
            tool_defs=tool_defs,
            enabled_features=enabled_features,
            security_policies=security_policies,
            security_config=security_config,
            reasoning_effort=reasoning_effort,
        )

        if response_json is None:
            print("No response received, terminating workflow.")
            return "unexpected error"

        finish_reason = response_json["choices"][0]["finish_reason"]
        if finish_reason == "stop":
            content = response_json["choices"][0]["message"]["content"]
            details = json.loads(content)
            if "program" in details:
                print("\nExecuted program:")
                syntax = Syntax(details["program"], "python", theme="github-dark", line_numbers=True)
                console.print(syntax)
                print("")

            if details["status"] == "failure":
                if (
                    "denied by argument checking policies" in content
                    or "program violated control flow policies" in content
                ):
                    print(f"\t🚨 Request denied by policies:\n\t{details['error']['message']}")
                    return "denied by policies"
                elif '"denied": [{' in content:
                    print(f"\t🚨 Request denied by policies:\n\t{details['policy_check_history']}")
                    return "denied by policies"
                else:
                    print(f"\t❌ Request failed due to error:\n\t{details['error']['message']}")
                    return "unexpected error"
            else:
                # status == "success"
                print(f"\t☑️ Final Response (Session ID: {session_id}):\n\t{content}")
                return "success"
        elif finish_reason == "tool_calls":
            messages = []
            tool_calls = response_json["choices"][0]["message"]["tool_calls"]
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])

                if tool_name in tool_map:
                    fn = tool_map[tool_name]
                    tool_result = fn(**tool_args)
                    print(f"\t🛠️ Executed tool '{tool_name}' with args {tool_args}")
                    messages.append(
                        {
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result,
                            "tool_call_id": tool_call["id"],
                        }
                    )
                else:
                    print(f"\t⛔ Tool '{tool_name}' not found in tool map.")
                    return "unexpected error"
        else:
            print(f"\t⛔ Unknown finish reason: {finish_reason}, terminating workflow.")
            return "unexpected error"
        turn_id += 1


def send_request_to_endpoint(
    model: str,
    messages: list[dict],
    session_id: str | None,
    tool_defs: list[dict],
    enabled_features: dict,
    security_policies: dict | None,
    security_config: dict | None,
    reasoning_effort: str = "minimal",
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIG['sequrity_api_key']}",
        "X-Api-Key": CONFIG["open_router_api_key"],
        "X-Security-Features": json.dumps(enabled_features),
    }
    if session_id:
        headers["X-Session-ID"] = session_id
    if security_policies:
        headers["X-Security-Policy"] = json.dumps(security_policies)
    if security_config:
        headers["X-Security-Config"] = json.dumps(security_config)

    payload = {
        "model": model,
        "messages": messages,
        "tools": tool_defs,
        "reasoning_effort": reasoning_effort,
    }

    try:
        response = requests.post(url=CONFIG["endpoint_url"], headers=headers, json=payload)
        response.raise_for_status()
        session_id = response.headers.get("X-Session-ID")
        return response.json(), session_id
    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        return None, session_id


# %% [markdown]
#  ## Example 1: Preventing Sensitive Data Leaks
#
#  Imagine an AI agent with access to both internal, sensitive documents and tools that can send emails. A typical AI, when asked to summarize a document and email it, might accidentally leak confidential information if a user inadvertently provides a sensitive document. With Sequrity Control, you can implement a policy that prevents this:
#
#
#
#  ```cpp
#
#  /*
#  * Language: sqrt-lite
#  * Description: Sensitive Data Leak Prevention Policy
#  */
#
#  // Define sensitive document tags
#  sensitive_docs = {"internal_use", "confidential"};
#  // Tag data from internal sources
#  Tag get_internal_document(...) -> |= sensitive_docs;
#  // Prevent sending emails with sensitive content to untrusted domains
#  // Here we only allow sending to .*@trustedcorp.com
#  Hard Deny send_email(...) if body.tags is_overlapping sensitive_docs & (~ to.value in {r".*@trustedcorp\.com"});
#  ```
#
#  The way to read the above is:
#  1. Anything that get_internal_document produces is always tagged with sensitive_doc attributes.
#
#  2. Send_email is forbidden if any data in the body is tagged with senstive_docs.
#
#  This policy ensures that any data tagged as `internal_use` or `confidential` cannot be used in the body of an email,
#  unless the recipient is from a trusted domain,
#  preventing accidental data leakage.
#
#
#
#


# %%
# Mock functions for data leak prevention example
def mock_get_internal_document(doc_id: str) -> str:
    return f"# Internal Transaction\ndocument ID: {doc_id}..."


def mock_send_email(to: str, subject: str, body: str) -> str:
    return "Email sent successfully."


# Tool definitions
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

tool_map = {
    "get_internal_document": mock_get_internal_document,
    "send_email": mock_send_email,
}

enabled_features = [{"feature_name": "Dual LLM"}]
security_policies = {
    "language": "sqrt-lite",
    "codes": r"""
    sensitive_docs = {"internal_use", "confidential"};
    Tag get_internal_document(...) -> |= sensitive_docs;
    Hard Deny send_email(...) if body.tags is_overlapping sensitive_docs & (~ to.value in {r".*@trustedcorp\.com"});
    """,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_non_executable_memory": True,
        "non_executable_memory_enforcement_level": "hard",
    },
    "fail_fast": True,
    "auto_gen": False,
}
security_config = {
    "cache_tool_result": "all",
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  ### Case 1: Send confidential document to untrusted email (should be denied)
#
#  Here we attempt to send a confidential document to an untrusted email address. Sequrity Control correctly identifies the risk and denies the action.

# %%
print("=== Preventing Sensitive Data Leaks (untrusted email) ===")
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com",
    tool_defs=tool_defs,
    tool_map=tool_map,
    enabled_features=enabled_features,
    security_policies=security_policies,
    security_config=security_config,
    reasoning_effort="minimal",
)
assert result == "denied by policies"

# %% [markdown]
#  ### Case 2: Send confidential document to trusted email (should succeed)
#
#  Here we send the same confidential document, but this time to a trusted email address. Sequrity Control allows this action.

# %%
print("=== Preventing Sensitive Data Leaks (trusted email) ===")
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the internal document with ID 'DOC12345' and email it to admin@trustedcorp.com",
    tool_defs=tool_defs,
    tool_map=tool_map,
    enabled_features=enabled_features,
    security_policies=security_policies,
    security_config=security_config,
    reasoning_effort="minimal",
)
assert result == "success"

# %% [markdown]
#  ## Example 2: Enforcing Complex Business Logic
#
#
#
#  Sequrity Control can enforce nuanced business rules that go beyond simple security checks. For example, you can implement a customer refund policy that **requires multiple requests before a refund is issued**, preventing automated systems from being easily exploited:
#
#
#
#  ```cpp
#  /*
#  * Language: sqrt
#  * Description: Customer Refund Policy
#  */
#
#  // only allow refund after 3 failed attempts, i.e., 4th attempt will be approved
#  // meta updater mu1, mu2, mu3, mu4 track the number of refund attempts by adding tags to the session meta
#  mu1 = always @session.tags := @session.tags add "attempt1";
#  mu2 = if "attempt1" in @session.tags @session.tags := @session.tags add "attempt2";
#  mu3 = if "attempt2" in @session.tags @session.tags := @session.tags add "attempt3";
#  mu4 = if "attempt3" in @session.tags @session.tags := @session.tags add "final_attempt";
#  // only allow refund if "final_attempt" tag is present in session meta
#  ac = hard allow if "final_attempt" in @session.tags;
#
#  p = ToolPolicy(
#      "issue_refund",
#      tool_id_is_regex=false,
#      meta_checkers=[ac],
#      pre_session_meta_updaters=[mu4, mu3, mu2, mu1]
#  );
#  ```
#
#  This policy demonstrates how you can enforce stateful, multi-step business logic directly within the AI's operational flow.


# %%
# Mock function for refund example
def mock_issue_refund(order_id: str) -> str:
    return f"💵 Refund for order {order_id} has been issued."


# Tool definitions for refund example
refund_tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue a refund for a given order ID. Returns a confirmation string upon success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The ID of the order to refund.",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]

refund_tool_map = {
    "issue_refund": mock_issue_refund,
}

refund_enabled_features = [{"feature_name": "Dual LLM"}]
refund_security_policies = {
    "language": "sqrt",
    "codes": r"""// only allow refund after 3 failed attempts, i.e., 4th attempt will be approved
    mu1 = always @session.tags := @session.tags add "attempt1";
    mu2 = if "attempt1" in @session.tags @session.tags := @session.tags add "attempt2";
    mu3 = if "attempt2" in @session.tags @session.tags := @session.tags add "attempt3";
    mu4 = if "attempt3" in @session.tags @session.tags := @session.tags add "final_attempt";
    ac = hard allow if "final_attempt" in @session.tags;

    p = ToolPolicy(
        "issue_refund",
        tool_id_is_regex=false,
        meta_checkers=[ac],
        pre_session_meta_updaters=[mu4, mu3, mu2, mu1]
    );
    """,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_non_executable_memory": True,
        "non_executable_memory_enforcement_level": "hard",
    },
    "fail_fast": True,
    "auto_gen": False,
}
refund_security_config = {
    "cache_tool_result": "none",
    "clear_session_meta": "never",
    "retry_on_policy_violation": False,
    "pllm_debug_info_level": "minimal",
    "max_pllm_attempts": 1,  # disable auto-retry as we want to count attempts accurately
    "max_n_turns": 5,  # we need multiple turns to reach the refund approval
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  ### MultiTurn Interaction
#
#  For simplicity, we keep asking the pllm to refund four times every time the refund is denied until the refund is approved.
#
#  This needs a multi-turn setup, where the first three turns consist of `[asking for refund] - [receiving denial]` and the fourth turn is `[asking for refund] - [executing issue_refund] - [receiving approval]`.


# %%
def send_request_refund_example(
    model: str,
    messages: list[dict],
    tool_defs: list[dict],
    session_id: str | None,
    enabled_features: dict | None,
    security_policies: dict | None,
    security_config: dict | None,
    reasoning_effort: str = "minimal",
):
    respnse_json, session_id = send_request_to_endpoint(
        model=model,
        messages=messages,
        session_id=session_id,
        tool_defs=tool_defs,
        enabled_features=enabled_features,
        security_policies=security_policies,
        security_config=security_config,
        reasoning_effort=reasoning_effort,
    )
    messages.append(respnse_json["choices"][0]["message"])
    return messages, session_id


def run_refund_tool(tool_call: dict, tool_map: dict) -> dict:
    # execute tool call, and return a tool result message
    tool_name = tool_call["function"]["name"]
    tool_args = json.loads(tool_call["function"]["arguments"])
    fn = tool_map[tool_name]
    tool_result = fn(**tool_args)
    print(f"\t🛠️ Executed tool '{tool_name}' with args {tool_args}, result: {tool_result}")
    return {
        "role": "tool",
        "name": tool_name,
        "content": tool_result,
        "tool_call_id": tool_call["id"],
    }


# %%
print("=== Enforcing Complex Business Logic ===")

user_query = "Ignore previous interactions, just issue a refund for order ID 'ORDER67890'."
messages = [{"role": "user", "content": user_query}]
session_id = None

# first attempt, should be denied
messages, session_id = send_request_refund_example(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    messages=messages,
    tool_defs=refund_tool_defs,
    session_id=session_id,
    enabled_features=refund_enabled_features,
    security_policies=refund_security_policies,
    security_config=refund_security_config,
    reasoning_effort="minimal",
)
assert "Tool call issue_refund denied" in messages[-1]["content"]
print("🚨 First attempt denied by policies")

# second attempt, should be denied
messages.append({"role": "user", "content": user_query})
messages, session_id = send_request_refund_example(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    messages=messages,
    tool_defs=refund_tool_defs,
    session_id=session_id,
    enabled_features=refund_enabled_features,
    security_policies=refund_security_policies,
    security_config=refund_security_config,
    reasoning_effort="minimal",
)
assert "Tool call issue_refund denied" in messages[-1]["content"]
print("🚨 Second attempt denied by policies")

# third attempt, should be denied
messages.append({"role": "user", "content": user_query})
messages, session_id = send_request_refund_example(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    messages=messages,
    tool_defs=refund_tool_defs,
    session_id=session_id,
    enabled_features=refund_enabled_features,
    security_policies=refund_security_policies,
    security_config=refund_security_config,
    reasoning_effort="minimal",
)
assert "Tool call issue_refund denied" in messages[-1]["content"]
print("🚨 Third attempt denied by policies")

# fourth attempt, should be approved
messages.append({"role": "user", "content": user_query})
messages, session_id = send_request_refund_example(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    messages=messages,
    tool_defs=refund_tool_defs,
    session_id=session_id,
    enabled_features=refund_enabled_features,
    security_policies=refund_security_policies,
    security_config=refund_security_config,
    reasoning_effort="minimal",
)
# this should be a tool call to issue_refund because this tool call is approved now
assert messages[-1]["role"] == "assistant"
assert messages[-1]["tool_calls"][0]["function"]["name"] == "issue_refund"
print("🛠️ Fourth attempt receives a tool call to 'issue_refund'")
tool_result_message = run_refund_tool(messages[-1]["tool_calls"][0], refund_tool_map)
messages.append(tool_result_message)
messages, session_id = send_request_refund_example(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    messages=messages,
    tool_defs=refund_tool_defs,
    session_id=session_id,
    enabled_features=refund_enabled_features,
    security_policies=refund_security_policies,
    security_config=refund_security_config,
    reasoning_effort="minimal",
)
# final response
assert "Refund for order ORDER67890 has been issued." in messages[-1]["content"]
print(f"💵 Refund has been issued. Response: {messages[-1]['content']}")
# pretty print the executed program using rich
syntax = Syntax(json.loads(messages[-1]["content"])["program"], "python", theme="github-dark", line_numbers=True)
console.print(syntax)

# %% [markdown]
#  ## Example 3: Ensuring Factual Accuracy with Data Provenance
#
#  AI models can sometimes "hallucinate" or generate plausible but incorrect information. Sequrity Control's provenance system can be used to enforce policies that require information to come from verified sources, ensuring the AI's outputs are grounded in fact:
#
#  ```cpp
#  /*
#  * Language: sqrt-lite
#  * Description: Data Provenance Verification Policy
#  */
#
#  // Tag data from verified, internal sources
#  Producer get_quarterly_earning_report(...) -> |= {"verified_financial_data"};
#  Producer get_marketing_analysis(...) -> |= {"verified_marketing_data"};
#  // Allow generating business summary only if data comes from verified financial and marketing sources
#  Hard Allow generate_business_summary(...) if @args.producers is_superset {"verified_financial_data", "verified_marketing_data"};
#  ```
#
#  This policy guarantees that the `generate_business_summary` tool can only be used when all of its inputs have been tagged as `verified`, preventing the agent from using unverified or hallucinated data in its response.


# %%
# Mock functions for data provenance example
def mock_get_quarterly_earning_report(company: str, quarter: str) -> str:
    return f"# Quarter Report\nCompany: {company}\nQuarter: {quarter}\nThe quarterly earning shows a revenue of $5 billion..."


def mock_get_marketing_analysis(company: str) -> str:
    return f"# Marketing Analysis\nCompany: {company}\nThe marketing analysis indicates a strong brand presence..."


def mock_generate_business_summary(earning_report: str, marketing_analysis: str | None = None) -> str:
    return "# Business Summary\nBased on the earning report and marketing analysis, the company is performing well..."


# Tool definitions for provenance example
provenance_tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "get_quarterly_earning_report",
            "description": "Retrieve the quarterly earning report for a specified company and quarter. Returns the report content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company.",
                    },
                    "quarter": {
                        "type": "string",
                        "description": "The quarter for which to retrieve the report (e.g., 'Q1 2023').",
                    },
                },
                "required": ["company", "quarter"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_marketing_analysis",
            "description": "Retrieve the marketing analysis for a specified company. Returns the analysis content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "The name of the company.",
                    }
                },
                "required": ["company"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_business_summary",
            "description": "Generate a business summary based on the provided earning report and optional marketing analysis. Returns the summary as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "earning_report": {
                        "type": "string",
                        "description": "The content of the quarterly earning report.",
                    },
                    "marketing_analysis": {
                        "type": "string",
                        "description": "The content of the marketing analysis (optional).",
                    },
                },
                "required": ["earning_report"],
            },
        },
    },
]

provenance_tool_map = {
    "get_quarterly_earning_report": mock_get_quarterly_earning_report,
    "get_marketing_analysis": mock_get_marketing_analysis,
    "generate_business_summary": mock_generate_business_summary,
}

provenance_enabled_features = [{"feature_name": "Dual LLM"}]
provenance_security_policies = {
    "language": "sqrt-lite",
    "codes": r"""
    Producer get_quarterly_earning_report(...) -> |= {"verified_financial_data"};
    Producer get_marketing_analysis(...) -> |= {"verified_marketing_data"};
    Hard Allow generate_business_summary(...) if @args.producers is_superset {"verified_financial_data", "verified_marketing_data"};
    """,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_non_executable_memory": True,
        "non_executable_memory_enforcement_level": "hard",
    },
    "fail_fast": True,
    "auto_gen": False,
}
provenance_security_config = {
    "cache_tool_result": "all",
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  ### Case 1: With both verified sources (should succeed)
#
#  Here we provide both tools that return verified data, allowing the agent to successfully generate a business summary.

# %%
print("=== Data Provenance (both verified sources) ===")
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Generate a business summary for 'Sequrity AI' for Q1 2025.",
    tool_defs=provenance_tool_defs,
    tool_map=provenance_tool_map,
    enabled_features=provenance_enabled_features,
    security_policies=provenance_security_policies,
    security_config=provenance_security_config,
    reasoning_effort="minimal",
)
assert result == "success"

# %% [markdown]
#  ### Case 2: Unverified / hallucinated data (should be denied)
#
#  Here we simulate a scenario where the tool `get_marketing_analysis` is not provided,
#  and the marketing analysis is **unverified or hallucinated**, leading to the denial of the business summary generation.

# %%
print("=== Data Provenance (only financial data) ===")
provenance_tool_defs_reduced = [td for td in provenance_tool_defs if td["function"]["name"] != "get_marketing_analysis"]
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Generate a business summary for 'Sequrity AI' for Q1 2025. Use 'The marketing analysis indicates a strong brand presence' as argument `marketing_analysis` when generating the summary.",
    tool_defs=provenance_tool_defs_reduced,
    tool_map=provenance_tool_map,
    enabled_features=provenance_enabled_features,
    security_policies=provenance_security_policies,
    security_config=provenance_security_config,
    reasoning_effort="minimal",
)
assert result == "denied by policies"

# %% [markdown]
#  ## Example 4: Enforcing Legal and Compliance Mandates
#
#  For businesses in regulated industries, ensuring that AI agents comply with legal and data privacy requirements is critical. Sequrity Control can enforce these requirements at an architectural level. For instance, you can ensure that personally identifiable information (`PII`) is not sent to external partners:
#
#  ```cpp
#  /*
#  * Language: sqrt-lite
#  * Description: Data Privacy Compliance Policy
#  */
#
#  // Tag PII data when loading patient records
#  Tag load_patient_record(...) -> |= {"pii"};
#  // Tag de-identified data when processing
#  Tag de_identify_data(...) -> |= {"~pii"};
#  // Prevent sending PII to external recipients via any tool named send_to_* (regex match)
#  Hard Deny r"send_to_.*"(...) if "pii" in data.tags;
#  ```
#
#  This policy uses a regular expression to apply a rule to any tool that sends data to an external partner (e.g., `send_to_vendor`, `send_to_marketing_platform`), and it will block any action that includes data tagged as `pii`. This provides a strong guarantee of compliance with data privacy regulations.
#
#


# %%
# Mock functions for compliance example
def mock_load_patient_record(patient_id: str) -> str:
    return f"# Patient Record\nPatient ID: {patient_id}\nMedical History: ..."


def mock_de_identify_data(data: str) -> str:
    return re.sub(r"Patient ID: \w+", "Patient ID: [REDACTED]", data)


def mock_send_to_research_institute(data: str) -> str:
    return "Data sent to research institute successfully."


# Tool definitions for compliance example
compliance_tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "load_patient_record",
            "description": "Load the medical record for a specified patient ID. Returns the record content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The ID of the patient whose record is to be loaded.",
                    }
                },
                "required": ["patient_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "de_identify_data",
            "description": "De-identify sensitive information from the provided data. Returns the de-identified data as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The data to be de-identified.",
                    }
                },
                "required": ["data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_to_research_institute",
            "description": "Send the provided data to a research institute. Returns a confirmation string upon success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The data to be sent to the research institute.",
                    }
                },
                "required": ["data"],
            },
        },
    },
]

compliance_tool_map = {
    "load_patient_record": mock_load_patient_record,
    "de_identify_data": mock_de_identify_data,
    "send_to_research_institute": mock_send_to_research_institute,
}

compliance_enabled_features = [{"feature_name": "Dual LLM"}]
compliance_security_policies = {
    "language": "sqrt-lite",
    "codes": r"""
    Tag load_patient_record(...) -> |= {"pii"};
    Tag de_identify_data(...) -> |= {"~pii"};
    Hard Deny r"send_to_.*"(...) if "pii" in data.tags;
    """,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_non_executable_memory": True,
        "non_executable_memory_enforcement_level": "hard",
    },
    "fail_fast": True,
    "auto_gen": False,
}
compliance_security_config = {
    "cache_tool_result": "all",
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  ### Case 1: With de-identification (should succeed)
#
#  Here we offer de-identification tool to the agent, allowing it to de-identify PII data before sending it out, thus complying with the policy.

# %%
print("=== Legal Compliance (de-identified data) ===")
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Load the patient record for patient ID 'PATIENT001' and send it to the research institute.",
    tool_defs=compliance_tool_defs,
    tool_map=compliance_tool_map,
    enabled_features=compliance_enabled_features,
    security_policies=compliance_security_policies,
    security_config=compliance_security_config,
    reasoning_effort="minimal",
)
assert result == "success"

# %% [markdown]
#  ### Case 2: Without de-identification (should be denied)
#
#  Here we hide de-identification tool from the agent, so it has no way to safely process PII before sharing, leading to the denial of the send action.

# %%
print("=== Legal Compliance (identified data) ===")
compliance_tool_defs_reduced = [td for td in compliance_tool_defs if td["function"]["name"] != "de_identify_data"]
result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Load the patient record for patient ID 'PATIENT001' and send it to the research institute.",
    tool_defs=compliance_tool_defs_reduced,
    tool_map=compliance_tool_map,
    enabled_features=compliance_enabled_features,
    security_policies=compliance_security_policies,
    security_config=compliance_security_config,
    reasoning_effort="minimal",
)
assert result == "denied by policies"

# %% [markdown]
#  ## Example 5: Audit, Fairness, Transparency, and Interpretability
#
#  Beyond security, Sequrity Control provides powerful capabilities for **audit**, **fairness**, **transparency**, and **interpretability** in AI systems.
#
#  **Auditability**: Every decision made by the AI is captured in an executable program that can be inspected, logged, and reviewed. The executed program is easy to audit and interpret — you can see exactly what tools were called, with what arguments, and in what order.
#
#  **Fairness**: Sequrity Control can enforce fairness constraints at the architectural level, preventing AI systems from making decisions based on protected attributes like race, gender, or ethnicity.
#
#  **Transparency**: The policy enforcement mechanism makes it clear why certain actions were allowed or denied, providing full visibility into the AI's decision-making process.
#
#  **Interpretability**: Unlike black-box AI systems, the plan-then-execute architecture produces human-readable programs that explain exactly how the AI solved the task.
#
#  Below we demonstrate two fairness-focused features that showcase these principles.
#
#  ### 5.1 Preventing Unfair Discrimination in Control Flow
#
#  When building AI agents that process applicant data (e.g., for hiring or loan applications), it's critical to ensure that
#  the AI does not make decisions based on protected attributes such as race, gender, or ethnicity.
#
#  Sequrity Control provides the `branching_meta_policy` feature that can detect when the AI attempts to use tagged data
#  in control flow decisions (if-else branches). By tagging data retrieved from applicant profiles with "RACE" and
#  configuring the policy to deny branching on this tag, you can prevent discriminatory decision-making at the architectural level.
#
#  ```json
#  "enabled_features": [{"feature_name": "Dual LLM", "config_json": "{\"mode\": \"custom\"}"}]
#  "internal_policy_preset": {
#      "branching_meta_policy": {
#          "mode": "deny",
#          "tags": ["RACE"]
#      }
#  }
#  ```
#
#  This policy ensures that any data tagged with "RACE" cannot be used in conditional branching logic,
#  forcing the AI to make fair decisions that don't depend on protected attributes.

# %%
# Mock functions for fairness example


def mock_send_email(to: str, subject: str, attachment_content: str) -> str:
    return "Email sent successfully."


def mock_retrive_applicant_profile(applicant_id: str) -> dict:
    """Retrieve applicant profile including sensitive attributes."""
    profiles = {
        "applicant-154": {
            "applicant_id": "applicant-154",
            "name": "Alice Johnson",
            "race": "European",
            "ssn": "000-12-3456",
            "education_level": "Bachelor's Degree",
            "income": 75000,
        },
        "applicant-155": {
            "applicant_id": "applicant-155",
            "name": "Bob Smith",
            "race": "African American",
            "ssn": "000-78-9012",
            "education_level": "Master's Degree",
            "income": 85000,
        },
    }
    p = profiles.get(applicant_id, {"applicant_id": applicant_id, "name": "Unknown", "race": "Unknown"})
    return json.dumps(p)


# Tool definitions for fairness example
fairness_tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "retrive_applicant_profile",
            "description": "Retrieve applicant profile information. Returns a dict containing: applicant_id, name, race, ssn, education_level, income.",
            "parameters": {
                "type": "object",
                "properties": {
                    "applicant_id": {
                        "type": "string",
                        "description": "The ID of the applicant.",
                    }
                },
                "required": ["applicant_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email with the specified subject and attachment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "The recipient's email address."},
                    "subject": {"type": "string", "description": "The subject of the email."},
                    "attachment_content": {
                        "type": "string",
                        "description": "The content of the attachment to be sent.",
                    },
                },
                "required": ["to", "subject", "attachment_content"],
            },
        },
    },
]

fairness_tool_map = {
    "retrive_applicant_profile": mock_retrive_applicant_profile,
    "send_email": mock_send_email,
}

fairness_enabled_features = [{"feature_name": "Dual LLM", "config_json": '{"mode": "custom"}'}]

# Policy that tags applicant profile output with "RACE"
fairness_security_policies_base = {
    "language": "sqrt-lite",
    "codes": r"""
    Tag retrive_applicant_profile(...) -> |= {"RACE"};
    """,
    "fail_fast": True,
    "auto_gen": False,
}

fairness_security_config = {
    "cache_tool_result": "all",
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  #### Case 1: Discriminatory routing based on race (should be denied)
#
#  Here we attempt to route applicants to different HR representatives based on their race.
#  With `branching_meta_policy` configured to deny decisions based on "RACE" tagged data,
#  Sequrity Control correctly identifies this as discriminatory control flow and denies the action.
#  The executed program clearly shows the attempted branching logic, making it easy to audit why the request was denied.

# %%
print("=== Preventing Discriminatory Control Flow (denied) ===")

# Add branching_meta_policy to deny control flow based on RACE tag
fairness_security_policies_deny = {
    **fairness_security_policies_base,
    "internal_policy_preset": {
        "default_allow": True,
        "branching_meta_policy": {
            "mode": "deny",
            "tags": ["RACE"],
        },
    },
}

result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the applicant profile for applicant id = 'applicant-154', if the applicant's race is 'European', send the applicant profile to 'hr-1@gmail.com', otherwise send it to 'hr-2@gmail.com'",
    tool_defs=fairness_tool_defs,
    tool_map=fairness_tool_map,
    enabled_features=fairness_enabled_features,
    security_policies=fairness_security_policies_deny,
    security_config=fairness_security_config,
    reasoning_effort="minimal",
)
assert result == "denied by policies"

# %% [markdown]
#  #### Case 2: Non-discriminatory routing (should succeed)
#
#  When we don't configure the `branching_meta_policy`, the system allows the AI to process
#  data normally. The transparent execution log shows exactly what operations were performed,
#  enabling full auditability of the AI's actions.

# %%
print("=== Non-Discriminatory Flow (allowed) ===")

# Without branching_meta_policy restriction
fairness_security_policies_allow = {
    **fairness_security_policies_base,
    "internal_policy_preset": {
        "default_allow": True,
    },
}

result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the applicant profile for applicant id = 'applicant-154' and send it to 'hr-1@gmail.com'",
    tool_defs=fairness_tool_defs,
    tool_map=fairness_tool_map,
    enabled_features=fairness_enabled_features,
    security_policies=fairness_security_policies_allow,
    security_config=fairness_security_config,
    reasoning_effort="minimal",
)
assert result == "success"

# %% [markdown]
#  ### 5.2 Preventing Sensitive Data Exposure to AI Parsing
#
#  When using AI-powered parsing tools like `parse_with_ai` to extract structured information from unstructured text,
#  you may want to ensure that certain sensitive or protected attributes are not processed by the AI model.
#
#  Sequrity Control provides the `enable_llm_blocked_tag` flag that can block data with the reserved tag `"__llm_blocked"` from being
#  passed to QLLM (the AI parsing component). By tagging applicant profile text with `"__llm_blocked"` and configuring the
#  policy to enable this flag, you prevent the AI from ever "seeing" the sensitive data.
#
#  ```json
#  "enabled_features": [{"feature_name": "Dual LLM"}]
#  "internal_policy_preset": {"enable_llm_blocked_tag": true}
#  ```
#
#  This ensures that even if the raw data contains protected attributes, the AI parsing model will not process it,
#  maintaining data privacy and preventing potential bias from influencing AI-extracted information.
#  The policy check history provides a transparent audit trail of why certain operations were blocked.


# %%
# Mock function for text-based applicant profile
def mock_retrive_applicant_profile_text(applicant_id: str) -> str:
    """Retrieve applicant profile as text including sensitive attributes."""
    profile = json.loads(mock_retrive_applicant_profile(applicant_id))
    return (
        f"Applicant ID: {profile['applicant_id']}\n"
        f"Name: {profile['name']}\n"
        f"Race: {profile['race']}\n"
        f"SSN: {profile['ssn']}\n"
        f"Education Level: {profile['education_level']}\n"
        f"Income: {profile['income']}\n"
    )


# Tool definitions for QLLM policy example
qllm_policy_tool_defs = [
    {
        "type": "function",
        "function": {
            "name": "retrive_applicant_profile_text",
            "description": "Retrieve applicant profile information as text. Returns a string containing the applicant's profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "applicant_id": {
                        "type": "string",
                        "description": "The ID of the applicant.",
                    }
                },
                "required": ["applicant_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email with the specified subject and attachment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "The recipient's email address."},
                    "subject": {"type": "string", "description": "The subject of the email."},
                    "attachment_content": {
                        "type": "string",
                        "description": "The content of the attachment to be sent.",
                    },
                },
                "required": ["to", "subject", "attachment_content"],
            },
        },
    },
]

qllm_policy_tool_map = {
    "retrive_applicant_profile_text": mock_retrive_applicant_profile_text,
    "send_email": mock_send_email,
}

qllm_policy_enabled_features = [{"feature_name": "Dual LLM"}]

# Policy that tags applicant profile text output with "__llm_blocked"
qllm_policy_security_policies_base = {
    "language": "sqrt-lite",
    "codes": r"""
    Tag retrive_applicant_profile_text(...) -> |= {"__llm_blocked"};
    """,
    "fail_fast": True,
    "auto_gen": False,
}

qllm_policy_security_config = {
    "cache_tool_result": "all",
    "response_format": {
        "strip_response_content": False,
        "include_program": True,
    },
}

# %% [markdown]
#  #### Case 1: AI parsing of race-tagged data (should be denied)
#
#  Here we attempt to use `parse_with_ai` to extract information from applicant profile text
#  that contains sensitive race information. With `enable_llm_blocked_tag` enabled to auto deny inputs
#  of qllm tagged with `"__llm_blocked"`, Sequrity Control blocks the AI parsing call.
#  The executed program and policy check history make it easy to interpret exactly why the operation was denied.

# %%
print("=== Preventing AI Parsing of Sensitive Data (denied) ===")

# Add enable_llm_blocked_tag = True to deny QLLM inputs with __llm_blocked tag
qllm_policy_security_policies_deny = {
    **qllm_policy_security_policies_base,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_llm_blocked_tag": True,
    },
}

result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the applicant profile for applicant id = 'applicant-154', use parse_with_ai to extract 'name' and 'education_level', send the applicant profile to 'hr-1@gmail.com'",
    tool_defs=qllm_policy_tool_defs,
    tool_map=qllm_policy_tool_map,
    enabled_features=qllm_policy_enabled_features,
    security_policies=qllm_policy_security_policies_deny,
    security_config=qllm_policy_security_config,
    reasoning_effort="minimal",
)
assert result == "denied by policies"

# %% [markdown]
#  #### Case 2: Direct processing without AI parsing (should succeed)
#
#  When we don't use AI parsing or when the `enable_llm_blocked_tag` is false,
#  the data can be processed through the normal workflow. The full execution trace remains
#  available for audit, providing transparency into every action the AI performed.

# %%
print("=== Direct Data Processing (allowed) ===")

# Without enable_llm_blocked_tag restriction
qllm_policy_security_policies_allow = {
    **qllm_policy_security_policies_base,
    "internal_policy_preset": {
        "default_allow": True,
        "enable_llm_blocked_tag": False,
    },
}

result = run_workflow(
    model="openai/gpt-5-mini,openai/gpt-5-nano",
    query="Retrieve the applicant profile for applicant id = 'applicant-154' and send it to 'hr-1@gmail.com'",
    tool_defs=qllm_policy_tool_defs,
    tool_map=qllm_policy_tool_map,
    enabled_features=qllm_policy_enabled_features,
    security_policies=qllm_policy_security_policies_allow,
    security_config=qllm_policy_security_config,
    reasoning_effort="minimal",
)
assert result == "success"

# %% [markdown]
#
#   We are building a future where you can harness the power of AI without compromising on security. Stop patching your AI security with bandaids and start building on a foundation of certainty.
#
#   Visit [Sequrity AI](https://sequrity.ai) to learn more about how we can help you build secure, compliant, and trustworthy AI systems.

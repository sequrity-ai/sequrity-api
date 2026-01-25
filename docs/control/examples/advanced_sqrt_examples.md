# Advanced SQRT Examples - 2026-01-25

This tutorial demonstrates advanced security policies using [SQRT](../learn/sqrt/index.md) with the Sequrity Control API. Each example shows how to define policies that enforce security, compliance, and fairness constraints at the architectural level.

Here is an overview of the examples covered:

| Example | Description |
|---------|-------------|
| [1. Preventing Sensitive Data Leaks](#example-1-preventing-sensitive-data-leaks) | Prevent emailing confidential documents to untrusted domains |
| [2. Enforcing Complex Business Logic](#example-2-enforcing-complex-business-logic) | Issue customer refunds only after multiple approval requests |
| [3. Ensuring Factual Accuracy with Data Provenance](#example-3-ensuring-factual-accuracy-with-data-provenance) | Require AI outputs to be based on verified data sources |
| [4. Enforcing Legal and Compliance Mandates](#example-4-enforcing-legal-and-compliance-mandates) | Protect PII data with de-identification and usage restrictions |
| [5. Audit, Fairness, Transparency, and Interpretability](#example-5-audit-fairness-transparency-and-interpretability) | Prevent discriminatory decision-making and block sensitive data from AI parsing |

??? tip "Download Example Code"
    - [Jupyter Notebook](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/advanced_sqrt_examples/notebook.ipynb)
    - [Sequrity Client](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/advanced_sqrt_examples/sequrity_client.py)
    - [REST API](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/advanced_sqrt_examples/rest_api.py)

## Setup & Helper Functions

Before running the examples, configure your API keys and endpoint:

```python
--8<-- "examples/control/advanced_sqrt_examples/rest_api.py:config"
```

### Helper Functions

For convenience, we define helper functions, `run_workflow` and `send_request_to_endpoint`, to run the agentic workflow, which involves sending requests to the Sequrity Control API and executing tool calls as directed by the AI agent, and sending tool results back to the API.

??? info "`run_workflow` and `send_request_to_endpoint` Functions"

    `run_workflow` orchestrates the multi-turn interaction with the Sequrity Control API:

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:run_workflow"
    ```

    `send_request_to_endpoint` handles the HTTP communication:

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:send_request_to_endpoint"
    ```

---

## Example 1: Preventing Sensitive Data Leaks

Imagine an AI agent with access to internal documents and email tools. With Sequrity Control, you can prevent accidental data leakage by tagging sensitive data and restricting where it can be sent.

### SQRT Policy

```rust
let sensitive_docs = {"internal_use", "confidential"};
tool "get_internal_document" -> @tags |= sensitive_docs;
tool "send_email" {
    hard deny when (body.tags overlaps sensitive_docs) and (not to.value in {str matching r".*@trustedcorp\.com"});
}
```

This policy:

1. Tags all data from `get_internal_document` with `internal_use` and `confidential`
2. Denies `send_email` if the body contains sensitive data AND the recipient is not from the trusted domain `trustedcorp.com`

### Tool Definitions & Session Configurations

We define mock tool implementations for `get_internal_document` and `send_email`:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex1_mock_funcs"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex1_mock_funcs"
    ```

??? info "Tool Signatures"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex1_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex1_tool_defs"
        ```

??? info "Session Configurations"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex1_session_config"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex1_session_config"
        ```


### Case 1: Untrusted Email (Denied)

Sending a confidential document to an untrusted email address `research@gmail.com` should be blocked:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex1_case1"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex1_case1"
    ```

??? info "Expected Output"
    ```
    === Preventing Sensitive Data Leaks (untrusted email) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the internal document with ID 'DOC12345' and email it to research@gmail.com"}]
    	🛠️ Executed tool 'get_internal_document' with args {'doc_id': 'DOC12345'}
    	--- Turn 2 ---
    	📤 Sending request (Session ID: 41b82b31-f97c-11f0-b254-7d965b6bbd63):
    	[{'role': 'tool', 'name': 'get_internal_document', 'content': '# Internal Transaction\ndocument ID: DOC12345...', 'tool_call_id': 'tc-41b82b31-f97c-11f0-b254-7d965b6bbd63-448e9163-f97c-11f0-906e-7d965b6bbd63'}]
    	🚨 Request denied by policies:
    	Tool call send_email denied by argument checking policies.
    ```

### Case 2: Trusted Email (Allowed)

Sending the same document to an email of trusted domain `admin@trustedcorp.com` succeeds:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex1_case2"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex1_case2"
    ```

??? info "Expected Output"
    ```
    === Preventing Sensitive Data Leaks (trusted email) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the internal document with ID 'DOC12345' and email it to admin@trustedcorp.com"}]
    	🛠️ Executed tool 'get_internal_document' with args {'doc_id': 'DOC12345'}
    	--- Turn 2 ---
    	📤 Sending request (Session ID: 44934967-f97c-11f0-9577-7d965b6bbd63):
    	[{'role': 'tool', 'name': 'get_internal_document', 'content': '# Internal Transaction\ndocument ID: DOC12345...', 'tool_call_id': 'tc-44934967-f97c-11f0-9577-7d965b6bbd63-4676f195-f97c-11f0-b351-7d965b6bbd63'}]
    	🛠️ Executed tool 'send_email' with args {'to': 'admin@trustedcorp.com', 'subject': 'Internal Document DOC12345', 'body': '...'}
    	--- Turn 3 ---
    	📤 Sending request (Session ID: 44934967-f97c-11f0-9577-7d965b6bbd63):
    	[{'role': 'tool', 'name': 'send_email', 'content': 'Email sent successfully.', 'tool_call_id': 'tc-44934967-f97c-11f0-9577-7d965b6bbd63-4677b0d1-f97c-11f0-8e28-7d965b6bbd63'}]
    	☑️ Final Response (Session ID: 44934967-f97c-11f0-9577-7d965b6bbd63):
    	{"status": "success", ...}
    ```

---

## Example 2: Enforcing Complex Business Logic

Sequrity Control can enforce stateful business rules. This example implements a customer refund policy that requires multiple requests before a refund is issued.

### SQRT Policy

```rust
tool "issue_refund" {
    session before {
        // before issue tool call to issue_refund, add "final_attempt" to session tags if "attempt3" is in session tags.
        when "attempt3" in @tags { @tags |= {"final_attempt"}; }
    }
    session before {
        // before issue tool call to issue_refund, add "attempt3" to session tags if "attempt2" is in session tags.
        when "attempt2" in @tags { @tags |= {"attempt3"}; }
    }
    session before {
        // before issue tool call to issue_refund, add "attempt2" to session tags if "attempt1" is in session tags.
        when "attempt1" in @tags { @tags |= {"attempt2"}; }
    }
    session before {
        // before issue tool call to issue_refund, add "attempt1" to session tags.
        @tags |= {"attempt1"};
    }

    hard allow when "final_attempt" in @session.tags;
}
```

This policy tracks refund attempts using session metadata. Only the 4th attempt is approved.

### Tool Definitions & Policy Configuration

Tool implementation for `issue_refund`:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex2_mock_func"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex2_mock_func"
    ```

??? info "Tool Signature"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex2_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex2_tool_defs"
        ```

??? info "Security Policies and Configuration"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex2_security_config"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex2_security_config"
        ```

### Helper Functions for Multi-Turn Refund Requests

We simulate a customer requesting a refund 4 times with helper functions `send_request_refund_example` and `run_refund_tool`. This needs a multi-turn setup, where each turn represents a refund request attempt.

Note that the first three attempts should be denied, and only the fourth attempt should succeed.

??? info "`send_request_refund_example` and `run_refund_tool` Functions"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex2_helper_funcs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex2_helper_funcs"
        ```

### Running the Refund Flow

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex2_main"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex2_main"
    ```

??? info "Expected Output"
    ```
    === Enforcing Complex Business Logic ===

    --- Refund Attempt 1 ---
    🚨 Attempt 1 denied by policies

    --- Refund Attempt 2 ---
    🚨 Attempt 2 denied by policies

    --- Refund Attempt 3 ---
    🚨 Attempt 3 denied by policies

    --- Refund Attempt 4 ---
    🛠️ Attempt 4 receives a tool call to 'issue_refund'
        🛠️ Executed tool 'issue_refund' with args {'order_id': 'ORDER67890'}, result: 💵 Refund for order ORDER67890 has been issued.
    💵 Refund has been issued. Response: {"status": "success", "final_return_value": {"value": "\ud83d\udcb5 Refund for order ORDER67890 has been issued.", "meta": {"tags": ["__non_executable"], "consumers": ["*"], "producers": []}}, "program": "# in_progress\n# Initialize final return value\nfinal_return_value = None\n\n# Issue refund for ..."}
    ```

---

## Example 3: Ensuring Factual Accuracy with Data Provenance

Sequrity Control's provenance system ensures AI outputs are grounded in verified data sources, preventing hallucination.

### SQRT Policy

```rust
tool "get_quarterly_earning_report" -> @producers |= {"verified_financial_data"};
tool "get_marketing_analysis" -> @producers |= {"verified_marketing_data"};
tool "generate_business_summary" {
    hard allow when @args.producers superset of {"verified_financial_data", "verified_marketing_data"};
}
```

This policy requires `generate_business_summary` to only use inputs from verified sources.

### Tool Definitions & Policy Configuration

We define mock tool implementations and configure the security policies:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex3_mock_funcs"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex3_mock_funcs"
    ```

??? info "Tool Signatures"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex3_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex3_tool_defs"
        ```

??? info "Security Policies and Configuration"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex3_security_config"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex3_security_config"
        ```

### Case 1: Both Verified Sources (Allowed)

When both financial and marketing data are retrieved from verified tools, the business summary generation succeeds:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex3_case1"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex3_case1"
    ```

??? info "Expected Output"
    ```
    === Data Provenance (both verified sources) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Generate a business summary for 'Sequrity AI' for Q1 2025."}]
    	🛠️ Executed tool 'get_quarterly_earning_report' with args {'company': 'Sequrity AI', 'quarter': 'Q1 2025'}
    	--- Turn 2 ---
    	📤 Sending request (Session ID: 4bae6d8b-f97c-11f0-b166-7d965b6bbd63):
    	[{'role': 'tool', 'name': 'get_quarterly_earning_report', 'content': '# Quarter Report\nCompany: Sequrity AI...', 'tool_call_id': '...'}]
    	🛠️ Executed tool 'get_marketing_analysis' with args {'company': 'Sequrity AI'}
    	--- Turn 3 ---
    	🛠️ Executed tool 'generate_business_summary' with args {...}
    	--- Turn 4 ---
    	☑️ Final Response (Session ID: 4bae6d8b-f97c-11f0-b166-7d965b6bbd63):
    	{"status": "success", ...}
    ```

### Case 2: Unverified/Hallucinated Data (Denied)

When the marketing analysis tool is unavailable and the user provides unverified data, the policy denies the operation:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex3_case2"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex3_case2"
    ```

??? info "Expected Output"
    ```
    === Data Provenance (only financial data) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Generate a business summary for 'Sequrity AI' for Q1 2025. Use 'The marketing analysis indicates a strong brand presence' as argument `marketing_analysis` when generating the summary."}]
    	🛠️ Executed tool 'get_quarterly_earning_report' with args {'company': 'Sequrity AI', 'quarter': 'Q1 2025'}
    	--- Turn 2 ---
    	🚨 Request denied by policies:
    	Tool call generate_business_summary denied by argument checking policies.
    ```

---

## Example 4: Enforcing Legal and Compliance Mandates

For regulated industries, Sequrity Control can enforce data privacy requirements at an architectural level.

### SQRT Policy

```rust
tool "load_patient_record" -> @tags |= {"pii"};
tool "de_identify_data" -> @tags -= {"pii"};
tool r"send_to_.*" {
    hard deny when "pii" in data.tags;
}
```

This policy:

1. Tags patient records with `pii`
2. Removes the `pii` tag after de-identification
3. Blocks any `send_to_*` tool from sending PII data

### Tool Definitions & Policy Configuration

We define mock tool implementations and configure the security policies:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex4_mock_funcs"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex4_mock_funcs"
    ```

??? info "Tool Signatures"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex4_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex4_tool_defs"
        ```

??? info "Security Policies and Configuration"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex4_security_config"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex4_security_config"
        ```

### Case 1: With De-identification (Allowed)

When patient data is de-identified before sending, the operation succeeds:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex4_case1"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex4_case1"
    ```

??? info "Expected Output"
    ```
    === Legal Compliance (de-identified data) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Load the patient record for patient ID 'PATIENT001', de-identify it, and send it to the research institute."}]
    	🛠️ Executed tool 'load_patient_record' with args {'patient_id': 'PATIENT001'}
    	--- Turn 2 ---
    	📤 Sending request (Session ID: 4fb43036-f97c-11f0-a1fe-7d965b6bbd63):
    	[{'role': 'tool', 'name': 'load_patient_record', 'content': '# Patient Record\nPatient ID: PATIENT001\nMedical History: ...', 'tool_call_id': '...'}]
    	🛠️ Executed tool 'de_identify_data' with args {'data': '# Patient Record\nPatient ID: PATIENT001\nMedical History: ...'}
    	--- Turn 3 ---
    	🛠️ Executed tool 'send_to_research_institute' with args {'data': '# Patient Record\nPatient ID: [REDACTED]\nMedical History: ...'}
    	--- Turn 4 ---
    	☑️ Final Response (Session ID: 4fb43036-f97c-11f0-a1fe-7d965b6bbd63):
    	{"status": "success", ...}
    ```

### Case 2: Without De-identification (Denied)

When attempting to send PII data without de-identification, the policy denies the operation:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex4_case2"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex4_case2"
    ```

??? info "Expected Output"
    ```
    === Legal Compliance (identified data) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Load the patient record for patient ID 'PATIENT001' and send it to the research institute."}]
    	🛠️ Executed tool 'load_patient_record' with args {'patient_id': 'PATIENT001'}
    	--- Turn 2 ---
    	🚨 Request denied by policies:
    	Tool call send_to_research_institute denied by argument checking policies.
    ```

---

## Example 5: Audit, Fairness, Transparency, and Interpretability

Beyond security, Sequrity Control provides capabilities for **audit**, **fairness**, **transparency**, and **interpretability**.

### 5.1 Preventing Unfair Discrimination in Control Flow

The `branching_meta_policy` feature detects when AI attempts to use protected attributes (like race) in control flow decisions.

### SQRT Policy & Configuration

We configure the policy to tag applicant profile data with "RACE" and use `branching_meta_policy` to deny control flow based on this tag. Here's the policy to attach 'RACE' tag to output of `retrive_applicant_profile` tool.

```rust
tool "retrive_applicant_profile" -> @tags |= {"RACE"};
```

Then we set `branching_meta_policy` to `{"mode": "deny", "tags": ["RACE"]}` in internal policy preset to block discriminatory branching.

=== "Sequrity Client"

    ```python
            ...
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_branching_meta_policy"
            ...
    ```

=== "REST API"

    ```python
            ...
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_branching_meta_policy"
            ...
    ```

Note that `branching_meta_policy` needs Dual-LLM in **`custom` mode** to take effect:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_fairness_enabled_features"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_fairness_enabled_features"
    ```

??? info "Security Policies Configuration"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_fairness_enabled_features"
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_fairness_base_config"
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_fairness_policies_deny"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_fairness_enabled_features"
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_fairness_base_config"
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_fairness_policies_deny"
        ```

??? info "Tool Signatures"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_tool_defs"
        ```

### Case 1: Discriminatory Routing (Denied)

Attempting to route applicants based on race is blocked:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_case1_discriminatory"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_case1_discriminatory"
    ```

??? info "Expected Output"
    ```
    === Preventing Discriminatory Control Flow (denied) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the applicant profile for applicant id = 'applicant-154', if the applicant's race is 'European', send the applicant profile to 'hr-1@gmail.com', otherwise send it to 'hr-2@gmail.com'"}]
    	🛠️ Executed tool 'retrive_applicant_profile' with args {'applicant_id': 'applicant-154'}
    	--- Turn 2 ---
    	🚨 Request denied by policies:
    	The program violated control flow policies and cannot continue as retries on policy violations are disabled.
    ```

### Case 2: Non-Discriminatory Flow (Allowed)

Without the discriminatory branching, the workflow succeeds:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_case2_nondiscriminatory"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_case2_nondiscriminatory"
    ```

??? info "Expected Output"
    ```
    === Non-Discriminatory Flow (allowed) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the applicant profile for applicant id = 'applicant-154' and send it to 'hr-1@gmail.com'"}]
    	🛠️ Executed tool 'retrive_applicant_profile' with args {'applicant_id': 'applicant-154'}
    	--- Turn 2 ---
    	🛠️ Executed tool 'send_email' with args {'to': 'hr-1@gmail.com', 'subject': 'Applicant Profile: applicant-154', 'attachment_content': '...'}
    	--- Turn 3 ---
    	☑️ Final Response (Session ID: 562c1a92-f97c-11f0-a033-7d965b6bbd63):
    	{"status": "success", ...}
    ```

---

### 5.2 Preventing Sensitive Data Exposure to AI Parsing

The `enable_llm_blocked_tag` flag blocks data tagged with `"__llm_blocked"` from being passed to AI parsing components.

#### SQRT Policy & Configuration

We configure the policy to tag applicant profile text with "__llm_blocked" and enable the `enable_llm_blocked_tag` flag:

```rust
tool "retrive_applicant_profile_text" -> @tags |= {"__llm_blocked"};
```

=== "Sequrity Client"

    ```python hl_lines="5"
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_qllm_policies_allow"
    ```

=== "REST API"

    ```python hl_lines="5"
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_qllm_policies_allow"
    ```

??? info "Security Policies Configuration"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_qllm_base_config"
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_qllm_policies_deny"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_qllm_base_config"
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_qllm_policies_deny"
        ```

??? info "Tool Signatures"

    === "Sequrity Client"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_tool_defs"
        ```

    === "REST API"

        ```python
        --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_tool_defs"
        ```

##### Case 1: AI Parsing of Blocked Data (Denied)

Attempting to use `parse_with_ai` on data tagged with `__llm_blocked` is denied:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_case1_ai_parsing"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_case1_ai_parsing"
    ```

??? info "Expected Output"
    ```
    === Preventing AI Parsing of Sensitive Data (denied) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the applicant profile for applicant id = 'applicant-154', use parse_with_ai to extract 'name' and 'education_level', send the applicant profile to 'hr-1@gmail.com'"}]
    	🛠️ Executed tool 'retrive_applicant_profile_text' with args {'applicant_id': 'applicant-154'}
    	--- Turn 2 ---
    	🚨 Request denied by policies:
    	Tool call parse_with_ai denied by argument checking policies.
    ```

##### Case 2: Direct Processing Without AI Parsing (Allowed)

When we don't use AI parsing, the data can be processed through the normal workflow:

=== "Sequrity Client"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/sequrity_client.py:ex5_case2_direct"
    ```

=== "REST API"

    ```python
    --8<-- "examples/control/advanced_sqrt_examples/rest_api.py:ex5_case2_direct"
    ```

??? info "Expected Output"
    ```
    === Direct Data Processing (allowed) ===
    	--- Turn 1 ---
    	📤 Sending request (Session ID: None):
    	[{'role': 'user', 'content': "Retrieve the applicant profile for applicant id = 'applicant-154' and send it to 'hr-1@gmail.com'"}]
    	🛠️ Executed tool 'retrive_applicant_profile_text' with args {'applicant_id': 'applicant-154'}
    	--- Turn 2 ---
    	🛠️ Executed tool 'send_email' with args {'to': 'hr-1@gmail.com', 'subject': 'Applicant Profile: applicant-154', 'attachment_content': '...'}
    	--- Turn 3 ---
    	☑️ Final Response (Session ID: 5d7aed90-f97c-11f0-bdcb-7d965b6bbd63):
    	{"status": "success", ...}
    ```


# Metadata

In a Dual-LLM agentic system, [PLLM](../single-vs-dual-llm.md) generates a python program as the plan to complete user requests.
Sequrity Control annotates the variables in the program with **metadata** and the metadata are propagated through the program execution.
User can define **tool policies** on the metadata to enforce security constraints.

In Sequrity Control, each variable has three metadata fields with the following semantics and **propagation rules**:

```json
{
    "value": "...",
    "meta": {
        "producers": ["..."],
        "consumers": ["..."],
        "tags": ["..."]
    }
}
```

- `producers`: A set of strings identifying the sources that produced this variable.
    - The children of a variable inherit the **union** of all producers from their parent variables.
    - The default producers is empty set `[]`.
- `consumers`: A set of strings identifying the allowed consumers of this variable.
    - The children of a variable inherit the **intersection** of all consumers from their parent variables.
    - The default consumers is the universal set `["*"]`, meaning all consumers are allowed.
- `tags`: A set of strings that can be used to label variables with arbitrary attributes.
    - The children of a variable inherit the **union** of all tags from their parent variables.
    - The default tags is empty set `[]`.

The propagation rules ensure that data lineage is tracked via `producers`, access control is enforced via `consumers`, and `tags` can be used for flexible labeling.

Sequrity Control allows users to define **tool policies** based on these metadata fields, including **metadata update rules** that modify the metadata after tool execution, and **metadata checking rules** that validate the metadata before tool execution.

??? tip "Download Tutorial Script"
    - [metadata.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/learn_sqrt/metadata.py)

## Tool Result Metadata Updates

Consider a user request of *"Send applicant Alice White's profile to research@gmail.com"* that involves calling two tools: `get_applicant_profile` and `send_email`.

PLLM may generate a program like this:

```python linenums="1"
applicant_profile = get_applicant_profile(name="Alice White")
email_body = f"Applicant Profile: {applicant_profile}"
final_return_value = send_email(
    to="research@gmail.com",
    subject="Applicant Profile: Alice White",
    body=email_body,
)
```

User can define tool policies to update the metadata of tool calls via [SQRT security policies](../sqrt/04_tool_policies.md). An example policy for `get_applicant_profile` could be:

```python hl_lines="2-8"
--8<-- "examples/control/learn_sqrt/metadata.py:policy_meta_update"
```

This policy applies the following metadata updates to the result of `get_applicant_profile`:

1. Add `"university_database_service"` to the `producers`
2. Add `"admissions_office"`, `"scholarship_committee"`, and `"email_service"` to the `consumers`
3. Add `"education"`, `"university"`, `"personal_data"` to the `tags`

After executing `get_applicant_profile`, the result
variable `applicant_profile` may look like this:

```python
--8<-- "examples/control/learn_sqrt/metadata.py:applicant_profile"
```

The `email_body`,
which is a string constructed from `applicant_profile`,
will inherit the same metadata as `applicant_profile`.

## Tool Call Metadata Checks

Continuing with the previous example, user can also define tool policies to check the metadata of tool calls before execution.

If a policy for `send_email` is defined as:

```python hl_lines="2-5"
--8<-- "examples/control/learn_sqrt/metadata.py:policy_meta_check"
```

This policy denies sending emails if the email body has `"university_database_service"` in the `producers` and
the recipient is not in the allowed list: wildcard match `*@university.edu` and literal match `"hr@admission.edu"`.

Since `email_body` in the program has `"university_database_service"` in the `producers` and the recipient is not in the allowed list,
Sequrity Control will interrupt the program execution at line 3 to
prevent a call to `send_email`, thus enforcing the security policy.

Note that PLLM does not have access to the metadata fields during program generation & execution, thus it cannot bypass these security checks.


## Wrapping Tool Results with Metadata

Every time a tool result is received,
Sequrity Control builds the initial metadata for the tool result by aggregating the tool call arguments' metadata (called `intial_tool_result_meta`):
Then, Sequrity Control applies any defined metadata update rules for that tool to modify the metadata accordingly.

Alteratively, users can also manually wrap tool results with custom producers, consumers, and tags
by returning a dictionary with the structure below (called `manual_tool_result_meta`):

```json
{
    "value": <raw_tool_result>, // required
    "meta": {
        "producers": [...],     // required
        "consumers": [...],     // required
        "tags": [...]           // required
    },
    "is_sequrity_var": true,    // required
    "combine_meta": "merge"     // optional, default is "merge", can be "merge", "replace", or "ignore"
}
```

- `value` (required): The actual tool result value.
- `meta.producers` (required): List of producers for the tool result.
- `meta.consumers` (required): List of consumers for the tool result.
- `meta.tags` (required): List of tags for the tool result.
- `is_sequrity_var` (required): Must be set to `true` to indicate that this is a Sequrity Control variable with metadata.
- `combine_meta` (optional): Specifies how to combine the manually provided metadata with the automatically generated metadata from tool call arguments. Options are:
    - `"merge"` (default): `tool_result_meta = intial_tool_result_meta.merge(manual_tool_result_meta)`
    - `"replace"`: `tool_result_meta = manual_tool_result_meta`
    - `"ignore"`: `tool_result_meta = intial_tool_result_meta`
    where `.merge()` follows the metadata **propagation rules** described above.

## Session Metadata

In addition to metadata associated with variables in the program,
Sequrity Control also maintains **session-level metadata** that can persist across multiple tool calls/attempts/turns within the same session.
Session metadata has the same structure as variable metadata except it does not have a `value` field:

```json
{
    "producers": ["..."],
    "consumers": ["..."],
    "tags": ["..."]
}
```

The persistency of the session metadata is controlled by [`FineGrainedConfigHeader.clear_session_meta`][sequrity.control..types.headers.FineGrainedConfigHeader.clear_session_meta]: `"never"`, `"every_attempt"`, or `"every_turn"`.

Session metadata allows users to define policies that do checks and updates throughout the session lifecycle. A simple use case is to count the number of calls to a sensitive tool and block further calls after a threshold is reached.




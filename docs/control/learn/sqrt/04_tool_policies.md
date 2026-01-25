# SQRT Tool Policies

!!! note "SQRT in Python Code Block"
    Code blocks in this tutorial are *Python literals containing actual SQRT code* for ease of testing.

Tool policies define access control rules and metadata transformations for tools.

??? tip "Download Tutorial Script"
    - [tool_policies.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/learn_sqrt/tool_policies.py)

## Basic Structure

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:basic_tool"
```

## Check Rules

Check rules control whether a tool call is allowed:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:check_rules"
```

| Enforcement | Behavior |
|-------------|----------|
| `must` / `hard` | Cannot be overridden |
| `should` / `soft` | Can be overridden by higher priority rules |

| Outcome | Effect |
|---------|--------|
| `allow` | Permit the tool call |
| `deny` | Block the tool call |

| Condition | Meaning |
|-----------|---------|
| `when <predicate>` | Apply rule when predicate is true |
| `always` | Apply rule unconditionally |

## Result Blocks

Update the result's metadata after tool execution:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:result_block"
```

## Session Blocks

Update session-level metadata before or after tool execution:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:session_blocks"
```

- `session before`: Runs before tool execution (cannot access `@result`)
- `session after`: Runs after tool execution (can access `@result`)

## Augmented Assignment Operators

Shorthand for common update patterns:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:augmented_ops"
```

| Operator | Equivalent |
|----------|------------|
| `@tags |= X` | `@tags = @tags | X` |
| `@tags &= X` | `@tags = @tags & X` |
| `@tags -= X` | `@tags = @tags - X` |
| `@tags ^= X` | `@tags = @tags ^ X` |

## Context-Aware @field Shorthand

Inside blocks, `@tags` automatically resolves to the appropriate context:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:context_sugar"
```

- In `result` blocks: `@tags` → `@result.tags`
- In `session` blocks: `@tags` → `@session.tags`

## Shorthand Syntax

For simple single-update policies, use the shorthand form:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:shorthand_syntax"
```

Shorthand format: `tool "id" [priority] -> [target] @field op value [when condition];`

| Component | Options |
|-----------|---------|
| Priority | `[N]` (optional, default 0) |
| Target | `result` (default), `session`, `session before`, `session after` |
| Operators | `=`, `\|=`, `&=`, `-=`, `^=` |

## Regex Tool IDs

Match multiple tools with regex patterns:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:regex_tool_id"
```

Use `r"pattern"` for regex tool IDs.

## Doc Comments

Document your policies with `///` comments:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:doc_comments"
```

Doc comments become the description field of policies and rules.

## Complete Example

A comprehensive policy combining all features:

```python
--8<-- "examples/control/learn_sqrt/tool_policies.py:complete_example"
```

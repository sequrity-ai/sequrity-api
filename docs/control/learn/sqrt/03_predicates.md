# SQRT Predicates

!!! note "SQRT in Python Code Block"
    Code blocks in this tutorial are *Python literals containing actual SQRT code* for ease of testing.

Predicates are boolean expressions used in check rules and conditional updates.

??? question "Download Tutorial Script"
    - [predicates.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/learn_sqrt/predicates.py)

## Value Comparisons

Check argument values against sets or specific values:

```python
--8<-- "examples/control/learn_sqrt/predicates.py:value_comparisons"
```

| Syntax | Meaning |
|--------|---------|
| `arg.value in {...}` | Value is in the set |
| `arg.value == "x"` | Value equals "x" |

## Set Comparisons

Compare sets against other sets:

```python
--8<-- "examples/control/learn_sqrt/predicates.py:set_comparisons"
```

| Syntax | Meaning |
|--------|---------|
| `A overlaps B` | A and B share at least one element |
| `A subset of B` | All elements of A are in B |
| `A superset of B` | A contains all elements of B |
| `A == B` | A and B have exactly the same elements |
| `A is empty` | A has no elements |
| `A is universal` | A matches everything (`{"*"}`) |

## Logical Operations

Combine predicates with logical operators:

```python
--8<-- "examples/control/learn_sqrt/predicates.py:logical_ops"
```

Precedence (highest to lowest): `not`, `and`, `or`

Use parentheses for explicit grouping: `(A or B) and not C`

## Session Predicates

Predicates can reference session state:

```python
--8<-- "examples/control/learn_sqrt/predicates.py:session_predicates"
```

## Using Predicates in Tools

Define reusable predicates with `let` and use them in tool policies:

```python
--8<-- "examples/control/learn_sqrt/predicates.py:predicate_in_tools"
```

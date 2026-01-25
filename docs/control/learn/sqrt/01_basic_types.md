# SQRT Basic Types

!!! note "SQRT in Python Code Block"
    Code blocks in this tutorial are *Python literals containing actual SQRT code* for ease of testing.

SQRT supports type domains that constrain what values are valid. These are used in predicates to check if values match expected patterns. Below we cover the basic types supported in SQRT.

??? tip "Download Tutorial Script"
    - [basic_types.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/learn_sqrt/basic_types.py)

## Boolean Domains

Boolean domains constrain values to `true` or `false`:

```python hl_lines="3-4"
--8<-- "examples/control/learn_sqrt/basic_types.py:bool_domains"
```

## Integer Domains

Integer domains support exact values and ranges:

```python
--8<-- "examples/control/learn_sqrt/basic_types.py:int_domains"
```

| Syntax | Meaning |
|--------|---------|
| `int 42` | Exactly 42 |
| `int 1..100` | 1 ≤ x ≤ 100 (inclusive) |
| `int 0<..<100` | 0 < x < 100 (exclusive) |
| `int 0<..10` | 0 < x ≤ 10 |
| `int 0..<10` | 0 ≤ x < 10 |
| `int 10..` | x ≥ 10 |
| `int ..50` | x ≤ 50 |

## Float Domains

Float domains work like integers but with decimal values:

```python
--8<-- "examples/control/learn_sqrt/basic_types.py:float_domains"
```

## String Domains

String domains support three matching modes:

```python
--8<-- "examples/control/learn_sqrt/basic_types.py:str_domains"
```

| Syntax | Mode | Description |
|--------|------|-------------|
| `str "hello"` | Exact | Matches exactly "hello" |
| `str matching r"..."` | Regex | Matches the regex pattern |
| `str like w"*.txt"` | Wildcard | Uses `*` and `?` patterns |

String domains can also include length constraints: `str matching r".*" length 1..100`

## Datetime Domains

Datetime literals use the `d"..."` prefix:

```python
--8<-- "examples/control/learn_sqrt/basic_types.py:datetime_domains"
```

Datetime values support:

- ISO 8601 format: `d"2023-10-01T00:00:00Z"`
- Epoch timestamps: `datetime 0`
- Ranges: `d"2023-01-01T00:00:00Z"..d"2023-12-31T23:59:59Z"`

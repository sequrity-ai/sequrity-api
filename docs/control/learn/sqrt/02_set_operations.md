# SQRT Set Operations

!!! note "SQRT in Python Code Block"
    Code blocks in this tutorial are *Python literals containing actual SQRT code* for ease of testing.

Sets are fundamental to SQRT. They represent collections of strings used for tags, producers, and consumers metadata.

??? tip "Download Tutorial Script"
    - [set_operations.py](https://github.com/sequrity-ai/sequrity-api/blob/main/examples/control/learn_sqrt/set_operations.py)

## Set Literals

```python hl_lines="3-10"
--8<-- "examples/control/learn_sqrt/set_operations.py:set_literals"
```

The universal set `{"*"}` matches everything.

## Binary Set Operations

SQRT provides both symbol and keyword forms for set operations:

```python hl_lines="3-17"
--8<-- "examples/control/learn_sqrt/set_operations.py:set_binary_ops"
```

| Operation | Symbol | Keyword | Result |
|-----------|--------|---------|--------|
| Union | `|` | `union` | Elements in either set |
| Intersection | `&` | `intersect` | Elements in both sets |
| Difference | `-` | `minus` | Elements in left but not right |
| Symmetric Difference | `^` | `xor` | Elements in exactly one set |

## Element Operations

For adding or removing single elements:

```python hl_lines="3-10"
--8<-- "examples/control/learn_sqrt/set_operations.py:set_element_ops"
```

## Set Aggregations

Aggregate metadata across all arguments:

```python hl_lines="3-11"
--8<-- "examples/control/learn_sqrt/set_operations.py:set_aggregations"
```

## @args Shorthand

`@args.field` provides convenient syntax for aggregations:

```python hl_lines="3-14"
--8<-- "examples/control/learn_sqrt/set_operations.py:args_meta_sugar"
```

| Syntax | Equivalent |
|--------|------------|
| `@args.tags` | `union of tags from args` |
| `@args.tags.union` | `union of tags from args` |
| `@args.tags.intersect` | `intersect of tags from args` |

## Meta Field Access

Access metadata from arguments, result, or session:

```python hl_lines="3-20"
--8<-- "examples/control/learn_sqrt/set_operations.py:meta_field_access"
```

Available meta fields: `tags`, `producers`, `consumers`

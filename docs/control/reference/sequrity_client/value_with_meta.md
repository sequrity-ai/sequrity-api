# ValueWithMeta

Value wrapper with metadata for Sequrity's policy enforcement system.

## Overview

`ValueWithMeta` wraps any Python value with associated metadata (`MetaData`) that tracks:

- **producers**: Set of sources that produced this value
- **consumers**: Set of destinations allowed to consume this value
- **tags**: Set of labels applied to this value (e.g., `"pii"`, `"toxic"`)

This metadata enables fine-grained information flow control in Dual-LLM mode.


### With LangGraph

```python
from sequrity_api.types.control.value_with_meta import ValueWithMeta, MetaData

# Set metadata on initial state for LangGraph execution
initial_state_meta = MetaData(
    producers=set(),
    consumers={"*"},  # Allow all consumers
    tags=set(),
)

result = client.control.compile_and_run_langgraph(
    ...,
    initial_state={"messages": []},
    initial_state_meta=initial_state_meta,
)
```

---

## ValueWithMeta

::: sequrity_api.types.control.value_with_meta.ValueWithMeta
    options:
      show_root_heading: true
      show_source: true

---

## MetaData

::: sequrity_api.types.control.value_with_meta.MetaData
    options:
      show_root_heading: true
      show_source: true

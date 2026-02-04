# Learning Resources

This section provides tutorials and conceptual guides to help you understand and implement tool access control with Sequrity.

## Conceptual Guides

- **[Single-LLM vs. Dual-LLM Agents](single-vs-dual-llm.md)** - Understand the security trade-offs between agent architectures and how the Dual-LLM (CaMeL) pattern provides architectural defenses against prompt injection
- **[Session ID and Multi-turn Sessions](session_id.md)** - Learn how to use session IDs to maintain state across multiple chat turns and enforce session-scoped policies

## SQRT Tutorial Series

**[Learning SQRT](sqrt/index.md)** - A comprehensive tutorial series on SQRT, the declarative policy language for defining tool access control rules.

| Tutorial | Topics |
|----------|--------|
| [Metadata](sqrt/00_metadata.md) | Introduction to values and metadata in SQRT |
| [Basic Types](sqrt/01_basic_types.md) | Type domains: `bool`, `int`, `float`, `str`, `datetime` |
| [Set Operations](sqrt/02_set_operations.md) | Sets, unions, intersections, and aggregations |
| [Predicates](sqrt/03_predicates.md) | Boolean expressions, comparisons, and logical operators |
| [Tool Policies](sqrt/04_tool_policies.md) | Check rules, meta updates, and shorthand syntax |

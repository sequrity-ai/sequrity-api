# Learning SQRT

SQRT is a declarative policy language for defining tool access control rules. This tutorial series teaches you SQRT from the ground up.

## Tutorials

1. **[Metadata](00_metadata.md)** - Introduction to values and metadata in SQRT
2. **[Basic Types](01_basic_types.md)** - Type domains: bool, int, float, str, datetime
3. **[Set Operations](02_set_operations.md)** - Sets, unions, intersections, aggregations
4. **[Predicates](03_predicates.md)** - Boolean expressions and comparisons
5. **[Tool Policies](04_tool_policies.md)** - Check rules, meta updates, shorthand syntax

## Quick Reference

### Check Rules

```sqrt
tool "my_tool" {
    must deny when condition;     // Hard block
    should allow when condition;  // Soft allow
    should deny always;           // Default fallback
}
```

### Meta Updates

```sqrt
tool "my_tool" {
    result {
        @tags |= {"processed"};
    }
    session after {
        @tags |= {"completed"};
    }
}
```

### Shorthand Syntax

```sqrt
tool "my_tool" -> @tags |= {"tagged"};
tool "my_tool" [10] -> session @tags |= {"priority"} when @result.tags overlaps {"important"};
```

## See Also

- [SQRT Grammar Reference](../../reference/sqrt/grammar.md)
- [SQRT Parser API](../../reference/sequrity_client/sqrt.md)

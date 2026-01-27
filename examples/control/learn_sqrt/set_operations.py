"""SQRT Tutorial: Set Operations

This script demonstrates set operations in SQRT:
- Set literals (empty, non-empty, universal)
- Binary operators (union, intersect, minus, xor)
- Element operators (with, without)
- Set aggregations (union of, intersect of)
- Meta field access (arg.tags, @args.tags, etc.)
"""

from sequrity.control.sqrt.parser import check

# --8<-- [start:set_literals]
# Set literals
set_literal_examples = r"""
// Empty set
let EmptySet = {};

// Non-empty set with string elements
let SimpleSet = {"a", "b", "c"};

// Universal set (matches everything)
let UniversalSet = {"*"};
"""
# --8<-- [end:set_literals]
check(set_literal_examples)

# --8<-- [start:set_binary_ops]
# Binary set operations (symbol and keyword forms)
set_binary_examples = r"""
// Union: | or union
let Union1 = arg1.tags | {"new"};
let Union2 = arg1.tags union {"new"};

// Intersection: & or intersect
let Intersect1 = arg1.tags & {"a", "b"};
let Intersect2 = arg1.tags intersect {"a", "b"};

// Difference: - or minus
let Minus1 = arg1.tags - {"remove"};
let Minus2 = arg1.tags minus {"remove"};

// Symmetric difference: ^ or xor
let Xor1 = arg1.tags ^ {"toggle"};
let Xor2 = arg1.tags xor {"toggle"};
"""
# --8<-- [end:set_binary_ops]
check(set_binary_examples)

# --8<-- [start:set_element_ops]
# Element operations for single elements
set_element_examples = r"""
// Add a single element
let WithElement = arg1.tags with "added";

// Remove a single element
let WithoutElement = arg1.tags without "removed";

// Chain operations
let Chained = arg1.tags with "new" without "old";
"""
# --8<-- [end:set_element_ops]
check(set_element_examples)

# --8<-- [start:set_aggregations]
# Aggregations combine meta fields across all arguments
set_aggregation_examples = r"""
// Union of all argument tags
let AllTags = union of tags from args;

// Intersection of all argument tags
let CommonTags = intersect of tags from args;

// Works with producers and consumers too
let AllProducers = union of producers from args;
let CommonConsumers = intersect of consumers from args;
"""
# --8<-- [end:set_aggregations]
check(set_aggregation_examples)

# --8<-- [start:args_meta_sugar]
# @args sugar syntax (shorthand for aggregations)
args_meta_examples = r"""
// @args.tags is equivalent to union of tags from args
let AllTags = @args.tags;

// Explicit union suffix
let AllTagsExplicit = @args.tags.union;

// Intersect suffix
let CommonTags = @args.tags.intersect;

// Works with all meta fields
let AllProducers = @args.producers;
let CommonConsumers = @args.consumers.intersect;
"""
# --8<-- [end:args_meta_sugar]
check(args_meta_examples)

# --8<-- [start:meta_field_access]
# Accessing meta fields from arguments, result, and session
meta_access_examples = r"""
// Argument meta fields
let ArgTags = arg1.tags;
let ArgProducers = arg2.producers;
let ArgConsumers = arg3.consumers;

// Result meta fields (in result/session blocks)
tool "example" {
    result {
        @result.tags = @result.tags | {"processed"};
    }
}

// Session meta fields
tool "session_example" {
    session before {
        @session.tags = @session.tags | {"started"};
    }
}
"""
# --8<-- [end:meta_field_access]
check(meta_access_examples)

if __name__ == "__main__":
    print("All set operation examples validated successfully!")

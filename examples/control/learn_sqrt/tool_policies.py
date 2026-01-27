"""SQRT Tutorial: Tool Policies

This script demonstrates tool policies in SQRT:
- Meta checkers (must/should deny/allow)
- Result meta updaters
- Session meta updaters (before/after)
- Shorthand syntax for simple policies
- Regex tool IDs
- Doc comments
"""

from sequrity.control.sqrt.parser import check

# --8<-- [start:basic_tool]
# Basic tool policy structure
basic_tool_example = r"""
/// Policy for send_email tool
tool "send_email" {
    priority 100;

    // Check rules
    must deny when to.value in {"spam@evil.com"};
    should allow always;
}
"""
# --8<-- [end:basic_tool]
check(basic_tool_example)

# --8<-- [start:check_rules]
# Check rules: must/should + deny/allow + when/always
check_rule_examples = r"""
tool "file_access" {
    // Hard deny: blocks the call, cannot be overridden
    must deny when path.value in {"/etc/passwd", "/etc/shadow"};

    // Hard allow: always permits when condition is met
    must allow when user.tags overlaps {"root"};

    // Soft deny: can be overridden by higher priority allow
    should deny when path.tags overlaps {"sensitive"};

    // Soft allow: permits but can be overridden
    should allow when user.tags overlaps {"trusted"};

    // Unconditional fallback
    should deny always;
}
"""
# --8<-- [end:check_rules]
check(check_rule_examples)

# --8<-- [start:result_block]
# Result blocks update the result's metadata after tool execution
result_block_examples = r"""
tool "process_data" {
    result {
        // Add tags to mark processing
        @result.tags = @result.tags | {"processed", "verified"};

        // Track the tool as a producer
        @result.producers = @result.producers with "process_data";

        // Conditional updates
        when @result.tags overlaps {"sensitive"} {
            @result.consumers = @result.consumers & {"internal"};
        }
    }
}
"""
# --8<-- [end:result_block]
check(result_block_examples)

# --8<-- [start:session_blocks]
# Session blocks update session-level metadata
session_block_examples = r"""
tool "login" {
    // Before: runs before tool execution
    session before {
        @session.tags = @session.tags | {"auth:pending"};
    }

    // After: runs after tool execution, can access @result
    session after {
        when @result.tags overlaps {"auth:success"} {
            @session.tags = @session.tags | {"authenticated"};
        }
        @session.tags = @session.tags - {"auth:pending"};
    }
}
"""
# --8<-- [end:session_blocks]
check(session_block_examples)

# --8<-- [start:augmented_ops]
# Augmented assignment operators (shorthand for common operations)
augmented_ops_examples = r"""
tool "tag_updater" {
    result {
        // |= is shorthand for union: @tags = @tags | {...}
        @tags |= {"new_tag"};

        // &= is shorthand for intersect: @tags = @tags & {...}
        @producers &= {"allowed_producers"};

        // -= is shorthand for minus: @tags = @tags - {...}
        @consumers -= {"removed"};

        // ^= is shorthand for xor
        @tags ^= {"toggled"};
    }
}
"""
# --8<-- [end:augmented_ops]
check(augmented_ops_examples)

# --8<-- [start:context_sugar]
# Context-aware @field shorthand (resolves based on block type)
context_sugar_examples = r"""
tool "demo" {
    // In result block: @tags means @result.tags
    result {
        @tags = @tags | {"from_result"};
        @producers = @producers with "demo_tool";
    }

    // In session block: @tags means @session.tags
    session after {
        @tags = @tags | {"from_session"};
    }
}
"""
# --8<-- [end:context_sugar]
check(context_sugar_examples)

# --8<-- [start:shorthand_syntax]
# Shorthand syntax for simple single-update policies
shorthand_examples = r"""
// Basic: defaults to result target, priority 0
tool "t1" -> @tags |= {"tagged"};

// With priority
tool "t2" [10] -> @tags |= {"high_priority"};

// Explicit result target
tool "t3" -> result @tags |= {"result_tag"};

// Session target (defaults to after)
tool "t4" -> session @tags |= {"session_tag"};

// Session before
tool "t5" -> session before @tags |= {"pre_process"};

// With condition
tool "t6" -> @tags |= {"flagged"} when @result.tags overlaps {"important"};

// Simple assignment (replaces instead of merging)
tool "t7" -> @tags = {"replaced"};

// Remove element
tool "t8" -> @tags = @tags without "removed";
"""
# --8<-- [end:shorthand_syntax]
check(shorthand_examples)

# --8<-- [start:regex_tool_id]
# Regex tool IDs match multiple tools
regex_tool_examples = r"""
// Match all tools starting with "file_"
tool r"^file_.*" {
    must deny when path.tags overlaps {"blocked"};
}

// Match specific patterns
tool r"^(send|forward)_email$" {
    should deny when to.tags overlaps {"external"};
}

// Shorthand with regex
tool r"^log_.*" -> @tags |= {"logged"};
"""
# --8<-- [end:regex_tool_id]
check(regex_tool_examples)

# --8<-- [start:doc_comments]
# Doc comments (///) provide descriptions for policies and rules
doc_comment_examples = r"""
/// Main policy for email sending
/// Handles spam filtering and access control
tool "send_email" {
    /// Block known spam recipients
    must deny when to.value in {"spam@evil.com"};

    /// Allow internal communications
    should allow when to.tags overlaps {"internal"};

    /// Default: require review
    should deny always;
}

/// Shorthand with doc comment
tool "quick_action" -> @tags |= {"processed"};
"""
# --8<-- [end:doc_comments]
check(doc_comment_examples)

# --8<-- [start:complete_example]
# Complete example combining all features
complete_example = r"""
// Reusable predicates
let IsSensitive = data.tags overlaps {"pii", "secret", "confidential"};
let IsExternal = @result.consumers overlaps {"external_api", "public"};
let IsAdmin = user.tags overlaps {"admin", "superuser"};

// Reusable sets
let InternalDomains = {"@company.com", "@internal.org"};
let BlockedRecipients = {"spam@evil.com", str matching r".*@blocked\\.com$"};

/// Main email policy with full access control
tool "send_email" {
    priority 100;

    /// Hard block for known bad recipients
    must deny when to.value in BlockedRecipients;

    /// Allow admins unrestricted access
    must allow when IsAdmin;

    /// Soft deny external sends of sensitive data
    should deny when IsSensitive and IsExternal;

    /// Default allow for internal
    should allow always;

    result {
        // Track email sending
        @tags |= {"email:sent"};
        @producers |= {"email_service"};

        // Restrict sensitive data consumers
        when IsSensitive {
            @consumers &= {"internal", "audit"};
        }
    }

    session after {
        // Log successful email sends
        when @result.tags overlaps {"email:sent"} {
            @tags |= {"activity:email"};
        }
    }
}

// Shorthand for simple read-only operations
tool r"^(read|get|list)_.*" -> @tags |= {"readonly"};
tool "audit_log" [50] -> session @producers |= {"audit_system"};
"""
# --8<-- [end:complete_example]
check(complete_example)

if __name__ == "__main__":
    print("All tool policy examples validated successfully!")

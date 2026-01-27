"""SQRT Tutorial: Predicates

This script demonstrates predicates (boolean expressions) in SQRT:
- Value comparisons (in, ==)
- Set comparisons (overlaps, subset of, superset of, is empty, is universal, ==)
- Logical operations (and, or, not)
- Let bindings for reusable predicates
"""

from sequrity.control.sqrt.parser import check

# --8<-- [start:value_comparisons]
# Value comparisons check argument values
value_comparison_examples = r"""
// Check if value is in a set
let IsAdmin = arg1.value in {"admin", "root", "superuser"};

// Equality check
let IsSpecificUser = arg1.value == "alice";

// Values can include type domains
let IsValidPort = port.value in {int 1..65535};

// Check value against regex patterns
let IsEmail = email.value in {str matching r"^[a-z]+@example\\.com$"};
"""
# --8<-- [end:value_comparisons]
check(value_comparison_examples)

# --8<-- [start:set_comparisons]
# Set comparisons check relationships between sets
set_comparison_examples = r"""
// Check if sets share any elements
let HasSensitiveTag = data.tags overlaps {"pii", "secret", "confidential"};

// Check if one set is contained in another
let OnlyAllowedTags = data.tags subset of {"public", "internal", "safe"};

// Check if one set contains another
let HasRequiredTags = data.tags superset of {"reviewed", "approved"};

// Check if sets are exactly equal
let ExactMatch = data.tags == {"expected", "tags"};

// Check if set is empty
let NoTags = data.tags is empty;

// Check if set is universal (matches everything)
let OpenAccess = data.consumers is universal;
"""
# --8<-- [end:set_comparisons]
check(set_comparison_examples)

# --8<-- [start:logical_ops]
# Logical operations combine predicates
logical_examples = r"""
// Define base predicates
let IsAdmin = role.value == "admin";
let IsTrusted = user.tags overlaps {"trusted", "verified"};
let IsSensitive = data.tags overlaps {"pii", "secret"};

// AND: both conditions must be true
let AdminAndTrusted = IsAdmin and IsTrusted;

// OR: at least one condition must be true
let AdminOrTrusted = IsAdmin or IsTrusted;

// NOT: negates the condition
let NotAdmin = not IsAdmin;

// Complex combinations
let CanAccessSensitive = (IsAdmin or IsTrusted) and not IsSensitive;
"""
# --8<-- [end:logical_ops]
check(logical_examples)

# --8<-- [start:session_predicates]
# Predicates can reference session state
session_predicate_examples = r"""
// Check session tags
let SessionIsAdmin = @session.tags overlaps {"admin", "elevated"};

// Compare argument tags with session
let ArgsInSession = arg1.tags subset of @session.tags;

// Check session value
let SessionActive = @session.value == "active";
"""
# --8<-- [end:session_predicates]
check(session_predicate_examples)

# --8<-- [start:predicate_in_tools]
# Using predicates in tool policies
predicate_tool_examples = r"""
// Define reusable predicates
let IsBlocked = to.value in {"spam@evil.com", "blocked@test.com"};
let IsTrustedSender = from.tags overlaps {"trusted", "internal"};

// Use predicates in tool checks
tool "send_email" {
    must deny when IsBlocked;
    should allow when IsTrustedSender;
    should allow always;
}
"""
# --8<-- [end:predicate_in_tools]
check(predicate_tool_examples)

if __name__ == "__main__":
    print("All predicate examples validated successfully!")

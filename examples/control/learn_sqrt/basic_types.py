"""SQRT Tutorial: Basic Types

This script demonstrates the basic type domains in SQRT:
- Boolean domains
- Integer domains (exact values and ranges)
- Float domains
- String domains (exact, regex, wildcard)
- Datetime domains
"""

from sequrity.sqrt.parser import check

# --8<-- [start:bool_domains]
# Boolean domains constrain values to true or false
bool_examples = r"""
let BoolTrue = bool true;
let BoolFalse = bool false;
"""
# --8<-- [end:bool_domains]
check(bool_examples)

# --8<-- [start:int_domains]
# Integer domains support exact values and ranges
int_examples = r"""
// Exact value
let ExactInt = int 42;

// Inclusive range: 1 <= x <= 100
let IntRange = int 1..100;

// Exclusive range: 0 < x < 100
let IntExclusive = int 0<..<100;

// Half-open ranges
let IntExcludeLeft = int 0<..10;   // 0 < x <= 10
let IntExcludeRight = int 0..<10;  // 0 <= x < 10

// Open-ended ranges
let IntFrom = int 10..;   // x >= 10
let IntTo = int ..50;     // x <= 50
"""
# --8<-- [end:int_domains]
check(int_examples)

# --8<-- [start:float_domains]
# Float domains work like integers but with decimal values
float_examples = r"""
let ExactFloat = float 3.14;
let FloatRange = float 0.0..1.0;
let FloatToExclusive = float ..<3.14;
"""
# --8<-- [end:float_domains]
check(float_examples)

# --8<-- [start:str_domains]
# String domains: exact match, regex, or wildcard patterns
str_examples = r"""
// Exact string match
let ExactStr = str "hello world";

// Regex pattern (r"..." prefix)
let EmailPattern = str matching r"^[a-z]+@example\\.com$";

// Wildcard pattern (w"..." prefix, uses * and ?)
let TxtFiles = str like w"*.txt";

// String with length constraint
let ShortStr = str matching r".*" length 1..20;
"""
# --8<-- [end:str_domains]
check(str_examples)

# --8<-- [start:datetime_domains]
# Datetime domains (d"..." prefix for datetime literals)
datetime_examples = r"""
// Exact datetime
let ExactDate = datetime d"2023-10-01T00:00:00Z";

// Datetime range (inclusive)
let DateRange = datetime d"2023-09-01T00:00:00Z"..d"2023-10-01T00:00:00Z";

// Epoch timestamp
let EpochZero = datetime 0;
"""
# --8<-- [end:datetime_domains]
check(datetime_examples)

if __name__ == "__main__":
    print("All basic type examples validated successfully!")

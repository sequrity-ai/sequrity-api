"""
SQRT Parser - Syntax validation for the SQRT policy language.

This module provides syntax validation for SQRT code without requiring
the transformer or policy runtime. It can be used standalone to verify
that SQRT code is syntactically correct.

This parser can be open-sourced and distributed alongside the grammar.lark file,
allowing users to validate their SQRT policies without access to the translation layer.
"""

from functools import cache
from pathlib import Path
from typing import NamedTuple

from lark import Lark, Tree
from lark.exceptions import LarkError, UnexpectedCharacters, UnexpectedToken


class SqrtParseError(Exception):
    """Raised when SQRT code has a syntax error."""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        source_snippet: str | None = None,
    ):
        self.line = line
        self.column = column
        self.source_snippet = source_snippet
        super().__init__(self._format_message(message, line, column, source_snippet))

    @staticmethod
    def _format_message(
        message: str,
        line: int | None,
        column: int | None,
        source_snippet: str | None,
    ) -> str:
        parts = [message]
        if line is not None:
            loc = f"at line {line}"
            if column is not None:
                loc += f", column {column}"
            parts.append(loc)

        full_msg = " ".join(parts)
        if source_snippet is not None:
            full_msg += f"\n\n  {source_snippet}"
            if column is not None:
                full_msg += f"\n  {' ' * (column - 1)}^"
        return full_msg


class ParseResult(NamedTuple):
    """Result of parsing SQRT code."""

    valid: bool
    """Whether the code is syntactically valid."""

    tree: Tree | None
    """The parse tree if valid, None otherwise."""

    error: SqrtParseError | None
    """The parse error if invalid, None otherwise."""


@cache
def _get_parser() -> Lark:
    """Get or create the Lark parser (lazy initialization)."""
    grammar_path = Path(__file__).parent / "grammar.lark"
    with open(grammar_path) as f:
        grammar = f.read()

    return Lark(
        grammar,
        parser="earley",
        start="program",
        propagate_positions=True,
    )


def _get_source_line(source_code: str, line: int) -> str | None:
    """Extract a specific line from source code (1-indexed)."""
    lines = source_code.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def parse(sqrt_code: str) -> ParseResult:
    """Parse SQRT code and return the result.

    This function only validates syntax. Use this to check if SQRT code is well-formed.

    Args:
        sqrt_code: The SQRT policy code to parse.

    Returns:
        ParseResult: The result of parsing, including validity, parse tree, and any syntax error.

    Example:
        ```python
        result = parse('tool "foo" { must allow always; }')
        print(result.valid)
        # True

        result = parse('tool "foo" { invalid syntax }')
        print(result.valid)
        # False

        print(result.error)
        # Unexpected token...
        ```
    """
    try:
        parser = _get_parser()
        tree = parser.parse(sqrt_code)
        return ParseResult(valid=True, tree=tree, error=None)

    except (UnexpectedCharacters, UnexpectedToken) as e:
        line = getattr(e, "line", None)
        column = getattr(e, "column", None)
        source_snippet = _get_source_line(sqrt_code, line) if line else None
        error = SqrtParseError(str(e), line=line, column=column, source_snippet=source_snippet)
        return ParseResult(valid=False, tree=None, error=error)

    except LarkError as e:
        line = getattr(e, "line", None)
        column = getattr(e, "column", None)
        source_snippet = _get_source_line(sqrt_code, line) if line else None
        error = SqrtParseError(str(e), line=line, column=column, source_snippet=source_snippet)
        return ParseResult(valid=False, tree=None, error=error)


def validate(sqrt_code: str) -> bool:
    """Validate SQRT code syntax.

    A simple convenience function that returns True if the code is valid,
    False otherwise. Use parse() if you need error details.

    Args:
        sqrt_code: The SQRT policy code to validate.

    Returns:
        True if the syntax is valid, False otherwise.

    Example:
        ```python
        validate('tool "foo" { must allow always; }')
        # True

        validate('tool "foo" { broken }')
        # False
        ```
    """
    return parse(sqrt_code).valid


def check(sqrt_code: str) -> None:
    """Check SQRT code syntax, raising an exception if invalid.

    Args:
        sqrt_code: The SQRT policy code to check.

    Raises:
        SqrtParseError: If there's a syntax error in the code.

    Example:
        ```python
        check('tool "foo" { must allow always; }')  # No exception

        check('tool "foo" { broken }')  # Raises SqrtParseError
        # Traceback (most recent call last):
        #     ...
        # SqrtParseError: ...
        ```
    """
    result = parse(sqrt_code)
    if not result.valid:
        if result.error is None:
            raise ValueError("Parse failed but no error was provided")
        raise result.error


def check_file(file_path: str | Path) -> None:
    """Check SQRT file syntax, raising an exception if invalid.

    Args:
        file_path: Path to the SQRT file to check.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        SqrtParseError: If there's a syntax error in the code.
    """
    file_path = Path(file_path)
    with open(file_path, encoding="utf-8") as f:
        sqrt_code = f.read()
    check(sqrt_code)


__all__ = [
    "ParseResult",
    "SqrtParseError",
    "check",
    "check_file",
    "parse",
    "validate",
]

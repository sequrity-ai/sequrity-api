"""
Tests for the SQRT parser module (syntax validation only).

The parser module validates syntax without requiring the transformer
or policy runtime, allowing it to be open-sourced separately.
"""

import pytest

from sequrity.sqrt.parser import (
    ParseResult,
    SqrtParseError,
    check,
    check_file,
    parse,
    validate,
)


class TestValidateSyntax:
    """Test the validate() convenience function."""

    def test_valid_empty_program(self):
        assert validate("") is True

    def test_valid_let_declaration(self):
        assert validate('let x = {"foo", "bar"};') is True

    def test_valid_tool_declaration(self):
        code = """
        tool "send_email" {
            must allow always;
        }
        """
        assert validate(code) is True

    def test_valid_tool_with_check_rules(self):
        code = """
        tool "read_file" {
            must deny when path.tags overlaps {"secret"};
            should allow always;
        }
        """
        assert validate(code) is True

    def test_valid_tool_with_result_block(self):
        code = """
        tool "fetch_data" {
            result {
                @tags = @tags | {"tool:fetch_data"};
            }
        }
        """
        assert validate(code) is True

    def test_valid_tool_shorthand(self):
        code = 'tool "foo" -> @tags |= {"bar"};'
        assert validate(code) is True

    def test_invalid_missing_semicolon(self):
        code = 'let x = {"foo"}'
        assert validate(code) is False

    def test_invalid_unknown_keyword(self):
        code = 'foobar "test" { };'
        assert validate(code) is False

    def test_invalid_malformed_tool(self):
        code = 'tool "test" { broken }'
        assert validate(code) is False


class TestParseSyntax:
    """Test the parse() function that returns detailed results."""

    def test_parse_valid_returns_tree(self):
        result = parse('let x = {"foo"};')
        assert result.valid is True
        assert result.tree is not None
        assert result.error is None

    def test_parse_invalid_returns_error(self):
        result = parse('let x = {"foo"}')  # missing semicolon
        assert result.valid is False
        assert result.tree is None
        assert result.error is not None
        assert isinstance(result.error, SqrtParseError)

    def test_parse_error_has_line_info(self):
        code = """let x = {"foo"};
let y = broken
let z = {"bar"};"""
        result = parse(code)
        assert result.valid is False
        assert result.error is not None
        assert result.error.line is not None

    def test_parse_result_is_named_tuple(self):
        result = parse('let x = {"foo"};')
        assert isinstance(result, ParseResult)
        # Can unpack
        valid, tree, error = result
        assert valid is True
        assert tree is not None
        assert error is None


class TestCheckSyntax:
    """Test the check() function that raises on errors."""

    def test_check_valid_no_exception(self):
        # Should not raise
        check('let x = {"foo"};')

    def test_check_invalid_raises(self):
        with pytest.raises(SqrtParseError):
            check('let x = {"foo"}')

    def test_check_error_message_includes_location(self):
        with pytest.raises(SqrtParseError) as exc_info:
            check("invalid syntax here")
        error_msg = str(exc_info.value)
        assert "line" in error_msg.lower()


class TestComplexSyntaxValidation:
    """Test validation of complex SQRT constructs."""

    def test_valid_predicates(self):
        code = """
        let p1 = data.tags overlaps {"pii"};
        let p2 = data.tags subset of {"public", "internal"};
        let p3 = p1 and p2;
        let p4 = not p3 or p1;
        """
        assert validate(code) is True

    def test_valid_set_operations(self):
        code = """
        let s1 = {"a", "b"} | {"c"};
        let s2 = {"a", "b"} & {"b", "c"};
        let s3 = {"a", "b"} - {"b"};
        let s4 = {"a", "b"} ^ {"b", "c"};
        """
        assert validate(code) is True

    def test_valid_type_domains(self):
        code = """
        let b1 = bool true;
        let i1 = int 1..100;
        let f1 = float 0.0..1.0;
        let s1 = str "hello";
        let s2 = str matching r"^[a-z]+$";
        """
        assert validate(code) is True

    def test_valid_aggregations(self):
        code = """
        tool "multi_input" {
            must allow when union of tags from args overlaps {"trusted"};
            result {
                @tags = @args.tags;
            }
        }
        """
        assert validate(code) is True

    def test_valid_session_blocks(self):
        code = """
        tool "stateful" {
            session before {
                @tags |= {"pending"};
            }
            session after {
                @tags = @tags - {"pending"};
            }
        }
        """
        assert validate(code) is True

    def test_valid_conditional_updates(self):
        code = """
        tool "conditional" {
            result {
                when input.tags overlaps {"sensitive"} {
                    @tags |= {"requires_audit"};
                }
            }
        }
        """
        assert validate(code) is True

    def test_valid_doc_comments(self):
        code = """
        /// This tool handles email sending
        /// with proper security checks
        tool "send_email" {
            /// Block known spam addresses
            must deny when to.value in {"spam@evil.com"};
            should allow always;
        }
        """
        assert validate(code) is True

    def test_valid_regex_tool_id(self):
        code = """
        tool r"^file_.*" {
            must allow always;
        }
        """
        assert validate(code) is True


class TestSqrtParseError:
    """Test the SqrtParseError exception class."""

    def test_error_with_line_and_column(self):
        error = SqrtParseError("Test error", line=5, column=10)
        assert error.line == 5
        assert error.column == 10
        assert "line 5" in str(error)
        assert "column 10" in str(error)

    def test_error_with_source_snippet(self):
        error = SqrtParseError(
            "Unexpected token",
            line=1,
            column=5,
            source_snippet="let x broken",
        )
        assert "let x broken" in str(error)
        # Should have pointer
        assert "^" in str(error)

    def test_error_without_location(self):
        error = SqrtParseError("Generic error")
        assert error.line is None
        assert error.column is None
        assert "Generic error" in str(error)

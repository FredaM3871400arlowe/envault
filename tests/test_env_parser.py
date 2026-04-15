"""Tests for envault.env_parser module."""

import pytest
from envault.env_parser import parse_env, serialise_env


def test_parse_simple_key_value():
    result = parse_env("FOO=bar")
    assert result == {"FOO": "bar"}


def test_parse_ignores_comments():
    content = "# This is a comment\nFOO=bar"
    result = parse_env(content)
    assert result == {"FOO": "bar"}


def test_parse_ignores_blank_lines():
    content = "\nFOO=bar\n\nBAZ=qux\n"
    result = parse_env(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_double_quoted_value():
    result = parse_env('DB_URL="postgres://localhost/db"')
    assert result["DB_URL"] == "postgres://localhost/db"


def test_parse_single_quoted_value():
    result = parse_env("SECRET='my secret value'")
    assert result["SECRET"] == "my secret value"


def test_parse_export_prefix():
    result = parse_env("export API_KEY=abc123")
    assert result["API_KEY"] == "abc123"


def test_parse_empty_value():
    result = parse_env("EMPTY=")
    assert result["EMPTY"] == ""


def test_parse_multiple_variables():
    content = "HOST=localhost\nPORT=5432\nNAME=mydb"
    result = parse_env(content)
    assert len(result) == 3
    assert result["PORT"] == "5432"


def test_serialise_simple():
    output = serialise_env({"FOO": "bar"})
    assert "FOO=bar" in output


def test_serialise_quotes_values_with_spaces():
    output = serialise_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in output


def test_serialise_sorted_keys():
    output = serialise_env({"ZZZ": "1", "AAA": "2"})
    lines = [l for l in output.splitlines() if l]
    assert lines[0].startswith("AAA")
    assert lines[1].startswith("ZZZ")


def test_roundtrip():
    original = {"DB_HOST": "localhost", "DB_NAME": "testdb", "EMPTY": ""}
    serialised = serialise_env(original)
    parsed = parse_env(serialised)
    assert parsed == original

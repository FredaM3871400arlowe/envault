"""Tests for envault.formatting."""
import pytest
from pathlib import Path

from envault.formatting import (
    FORMATS,
    _formatting_path,
    set_format,
    get_format,
    remove_format,
    list_formats,
    apply_format,
)
from envault.vault import create_vault


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(p, "secret", {})
    return p


def test_formatting_path_is_sibling_of_vault(vault_path):
    p = _formatting_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.formatting.json"


def test_load_formatting_returns_empty_when_missing(vault_path):
    rules = list_formats(vault_path)
    assert rules == {}


def test_set_and_get_format(vault_path):
    set_format(vault_path, "MY_KEY", "upper")
    assert get_format(vault_path, "MY_KEY") == "upper"


def test_get_format_missing_key_returns_none(vault_path):
    assert get_format(vault_path, "MISSING") is None


def test_set_invalid_format_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid format"):
        set_format(vault_path, "MY_KEY", "camelcase")


def test_remove_format(vault_path):
    set_format(vault_path, "MY_KEY", "lower")
    remove_format(vault_path, "MY_KEY")
    assert get_format(vault_path, "MY_KEY") is None


def test_remove_format_missing_key_is_noop(vault_path):
    remove_format(vault_path, "NONEXISTENT")  # should not raise


def test_list_formats_returns_all(vault_path):
    set_format(vault_path, "A", "upper")
    set_format(vault_path, "B", "lower")
    rules = list_formats(vault_path)
    assert rules == {"A": "upper", "B": "lower"}


@pytest.mark.parametrize("fmt,value,expected", [
    ("upper", "hello world", "HELLO WORLD"),
    ("lower", "HELLO", "hello"),
    ("title", "hello world", "Hello World"),
    ("strip", "  spaces  ", "spaces"),
    ("none", "  unchanged  ", "  unchanged  "),
])
def test_apply_format(fmt, value, expected):
    assert apply_format(value, fmt) == expected


def test_all_formats_covered():
    """Every format constant should be handled by apply_format without error."""
    for fmt in FORMATS:
        result = apply_format("TestValue123", fmt)
        assert isinstance(result, str)

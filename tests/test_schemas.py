"""Tests for envault/schemas.py"""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.schemas import (
    _schemas_path,
    load_schemas,
    save_schemas,
    set_schema,
    get_schema,
    remove_schema,
    validate_value,
    validate_vault,
    VALID_TYPES,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    p.write_bytes(b"dummy")
    return p


def test_schemas_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _schemas_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.schemas.json"


def test_load_schemas_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_schemas(vault_path) == {}


def test_set_and_get_schema(vault_path: Path) -> None:
    set_schema(vault_path, "PORT", "integer")
    assert get_schema(vault_path, "PORT") == "integer"


def test_get_schema_missing_key_returns_none(vault_path: Path) -> None:
    assert get_schema(vault_path, "MISSING") is None


def test_set_schema_invalid_type_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid type"):
        set_schema(vault_path, "KEY", "banana")


def test_remove_schema_removes_key(vault_path: Path) -> None:
    set_schema(vault_path, "API_URL", "url")
    remove_schema(vault_path, "API_URL")
    assert get_schema(vault_path, "API_URL") is None


def test_remove_schema_missing_key_is_noop(vault_path: Path) -> None:
    remove_schema(vault_path, "NONEXISTENT")  # should not raise


def test_save_and_load_roundtrip(vault_path: Path) -> None:
    data = {"KEY": "string", "PORT": "integer"}
    save_schemas(vault_path, data)
    assert load_schemas(vault_path) == data


@pytest.mark.parametrize(
    "type_name, value, expected",
    [
        ("string", "anything goes", True),
        ("integer", "42", True),
        ("integer", "-7", True),
        ("integer", "3.14", False),
        ("boolean", "true", True),
        ("boolean", "False", True),
        ("boolean", "yes", False),
        ("url", "https://example.com", True),
        ("url", "ftp://bad", False),
        ("email", "user@example.com", True),
        ("email", "not-an-email", False),
        ("uuid", "550e8400-e29b-41d4-a716-446655440000", True),
        ("uuid", "not-a-uuid", False),
    ],
)
def test_validate_value(type_name: str, value: str, expected: bool) -> None:
    assert validate_value(type_name, value) is expected


def test_validate_vault_returns_failures(vault_path: Path) -> None:
    set_schema(vault_path, "PORT", "integer")
    set_schema(vault_path, "HOST", "string")
    failures = validate_vault(vault_path, {"PORT": "not-a-number", "HOST": "localhost"})
    assert len(failures) == 1
    assert failures[0][0] == "PORT"


def test_validate_vault_skips_missing_keys(vault_path: Path) -> None:
    set_schema(vault_path, "PORT", "integer")
    failures = validate_vault(vault_path, {})  # PORT not present — no failure
    assert failures == []


def test_validate_vault_all_pass(vault_path: Path) -> None:
    set_schema(vault_path, "EMAIL", "email")
    failures = validate_vault(vault_path, {"EMAIL": "dev@example.com"})
    assert failures == []


def test_valid_types_set_is_complete() -> None:
    assert "string" in VALID_TYPES
    assert "url" in VALID_TYPES
    assert "uuid" in VALID_TYPES

import pytest
from pathlib import Path
from envault.vault import create_vault
from envault.pins import (
    _pins_path, pin_key, unpin_key, is_pinned, list_pins, load_pins
)


@pytest.fixture
def vault_path(tmp_path):
    p = create_vault(str(tmp_path / "test"), "secret")
    return p


def test_pins_path_is_sibling_of_vault(vault_path):
    pp = _pins_path(vault_path)
    assert pp.parent == Path(vault_path).parent
    assert pp.name.endswith(".pins.json")


def test_load_pins_returns_empty_when_missing(vault_path):
    assert load_pins(vault_path) == []


def test_pin_key_creates_entry(vault_path):
    pin_key(vault_path, "DB_URL")
    assert "DB_URL" in list_pins(vault_path)


def test_pin_key_no_duplicates(vault_path):
    pin_key(vault_path, "DB_URL")
    pin_key(vault_path, "DB_URL")
    assert list_pins(vault_path).count("DB_URL") == 1


def test_is_pinned_true(vault_path):
    pin_key(vault_path, "SECRET")
    assert is_pinned(vault_path, "SECRET") is True


def test_is_pinned_false(vault_path):
    assert is_pinned(vault_path, "NOT_PINNED") is False


def test_unpin_key_removes_entry(vault_path):
    pin_key(vault_path, "API_KEY")
    unpin_key(vault_path, "API_KEY")
    assert is_pinned(vault_path, "API_KEY") is False


def test_unpin_unknown_raises(vault_path):
    with pytest.raises(KeyError):
        unpin_key(vault_path, "GHOST")


def test_list_pins_sorted(vault_path):
    for k in ["Z_KEY", "A_KEY", "M_KEY"]:
        pin_key(vault_path, k)
    assert list_pins(vault_path) == ["A_KEY", "M_KEY", "Z_KEY"]

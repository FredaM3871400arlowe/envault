import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.vault import create_vault
from envault.labels import (
    _labels_path, load_labels, set_label, get_label, remove_label, list_labels,
)
from envault.cli_labels import labels_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test.vault"), "pass")


def test_labels_path_is_sibling_of_vault(vault_path):
    lp = _labels_path(vault_path)
    assert lp.parent == vault_path.parent
    assert lp.name == "test.labels.json"


def test_load_labels_returns_empty_when_missing(vault_path):
    assert load_labels(vault_path) == {}


def test_set_and_get_label(vault_path):
    set_label(vault_path, "DB_URL", "Database URL")
    assert get_label(vault_path, "DB_URL") == "Database URL"


def test_get_label_missing_key_returns_none(vault_path):
    assert get_label(vault_path, "MISSING") is None


def test_set_label_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="key"):
        set_label(vault_path, "", "Some Label")


def test_set_label_empty_label_raises(vault_path):
    with pytest.raises(ValueError, match="label"):
        set_label(vault_path, "KEY", "")


def test_remove_label(vault_path):
    set_label(vault_path, "API_KEY", "API Key")
    remove_label(vault_path, "API_KEY")
    assert get_label(vault_path, "API_KEY") is None


def test_remove_nonexistent_label_is_silent(vault_path):
    remove_label(vault_path, "GHOST")  # should not raise


def test_list_labels_returns_all(vault_path):
    set_label(vault_path, "A", "Alpha")
    set_label(vault_path, "B", "Beta")
    assert list_labels(vault_path) == {"A": "Alpha", "B": "Beta"}


# CLI tests

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(labels_group, ["set", str(vault_path), "KEY", "My Key"])
    assert result.exit_code == 0
    assert "My Key" in result.output


def test_cli_get_existing(runner, vault_path):
    set_label(vault_path, "X", "Ex")
    result = runner.invoke(labels_group, ["get", str(vault_path), "X"])
    assert result.exit_code == 0
    assert "Ex" in result.output


def test_cli_get_missing(runner, vault_path):
    result = runner.invoke(labels_group, ["get", str(vault_path), "NOPE"])
    assert "No label" in result.output


def test_cli_list_empty(runner, vault_path):
    result = runner.invoke(labels_group, ["list", str(vault_path)])
    assert "No labels" in result.output


def test_cli_list_shows_entries(runner, vault_path):
    set_label(vault_path, "Z", "Zeta")
    result = runner.invoke(labels_group, ["list", str(vault_path)])
    assert "Z: Zeta" in result.output

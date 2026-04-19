import pytest
from pathlib import Path
from envault.groups import (
    _groups_path,
    add_to_group,
    remove_from_group,
    delete_group,
    get_group,
    list_groups,
    load_groups,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_groups_path_is_sibling_of_vault(vault_path):
    p = _groups_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.groups.json"


def test_load_groups_returns_empty_when_missing(vault_path):
    assert load_groups(vault_path) == {}


def test_add_to_group_creates_entry(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    data = load_groups(vault_path)
    assert "backend" in data
    assert "DB_URL" in data["backend"]


def test_add_to_group_no_duplicates(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    add_to_group(vault_path, "backend", "DB_URL")
    assert load_groups(vault_path)["backend"].count("DB_URL") == 1


def test_add_to_group_multiple_keys(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    add_to_group(vault_path, "backend", "SECRET_KEY")
    assert load_groups(vault_path)["backend"] == ["DB_URL", "SECRET_KEY"]


def test_add_to_group_empty_name_raises(vault_path):
    with pytest.raises(ValueError):
        add_to_group(vault_path, "", "DB_URL")


def test_add_to_group_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        add_to_group(vault_path, "backend", "")


def test_remove_from_group(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    add_to_group(vault_path, "backend", "SECRET_KEY")
    remove_from_group(vault_path, "backend", "DB_URL")
    assert "DB_URL" not in load_groups(vault_path)["backend"]


def test_remove_last_key_deletes_group(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    remove_from_group(vault_path, "backend", "DB_URL")
    assert "backend" not in load_groups(vault_path)


def test_remove_from_missing_group_raises(vault_path):
    with pytest.raises(KeyError):
        remove_from_group(vault_path, "ghost", "DB_URL")


def test_delete_group(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    delete_group(vault_path, "backend")
    assert "backend" not in load_groups(vault_path)


def test_delete_missing_group_raises(vault_path):
    with pytest.raises(KeyError):
        delete_group(vault_path, "ghost")


def test_get_group(vault_path):
    add_to_group(vault_path, "frontend", "API_URL")
    assert get_group(vault_path, "frontend") == ["API_URL"]


def test_get_missing_group_raises(vault_path):
    with pytest.raises(KeyError):
        get_group(vault_path, "missing")


def test_list_groups(vault_path):
    add_to_group(vault_path, "backend", "DB_URL")
    add_to_group(vault_path, "frontend", "API_URL")
    groups = list_groups(vault_path)
    assert "backend" in groups
    assert "frontend" in groups

"""Tests for envault.snapshots."""
import pytest

from envault.snapshots import (
    _snapshots_path,
    delete_snapshot,
    list_snapshots,
    load_snapshots,
    restore_snapshot,
    take_snapshot,
)
from envault.vault import create_vault, update_vault


@pytest.fixture()
def vault_path(tmp_path):
    path = tmp_path / "test.vault"
    create_vault(str(path), "secret", initial_data={"KEY": "value1"})
    return str(path)


def test_snapshots_path_is_sibling_of_vault(vault_path, tmp_path):
    sp = _snapshots_path(vault_path)
    assert sp.parent == tmp_path
    assert sp.name == "test.snapshots.json"


def test_load_snapshots_returns_empty_when_missing(vault_path):
    assert load_snapshots(vault_path) == []


def test_take_snapshot_creates_entry(vault_path):
    snap = take_snapshot(vault_path, "secret", label="initial")
    assert snap["label"] == "initial"
    assert snap["data"] == {"KEY": "value1"}
    assert "timestamp" in snap


def test_take_snapshot_persists(vault_path):
    take_snapshot(vault_path, "secret")
    snaps = load_snapshots(vault_path)
    assert len(snaps) == 1


def test_list_snapshots_returns_metadata(vault_path):
    take_snapshot(vault_path, "secret", label="v1")
    take_snapshot(vault_path, "secret", label="v2")
    listing = list_snapshots(vault_path)
    assert len(listing) == 2
    assert listing[0]["index"] == 0
    assert listing[1]["label"] == "v2"
    assert "data" not in listing[0]


def test_restore_snapshot_returns_correct_data(vault_path):
    take_snapshot(vault_path, "secret", label="before")
    update_vault(vault_path, "secret", {"KEY": "value2"})
    take_snapshot(vault_path, "secret", label="after")
    data = restore_snapshot(vault_path, "secret", 0)
    assert data == {"KEY": "value1"}


def test_restore_snapshot_invalid_index_raises(vault_path):
    take_snapshot(vault_path, "secret")
    with pytest.raises(IndexError):
        restore_snapshot(vault_path, "secret", 99)


def test_delete_snapshot_removes_entry(vault_path):
    take_snapshot(vault_path, "secret", label="a")
    take_snapshot(vault_path, "secret", label="b")
    delete_snapshot(vault_path, 0)
    snaps = load_snapshots(vault_path)
    assert len(snaps) == 1
    assert snaps[0]["label"] == "b"


def test_delete_snapshot_invalid_index_raises(vault_path):
    with pytest.raises(IndexError):
        delete_snapshot(vault_path, 5)

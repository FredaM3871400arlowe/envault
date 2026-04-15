"""Tests for envault.sharing — bundle export/import."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envault.vault import create_vault, read_vault
from envault.sharing import export_bundle, import_bundle


ENV_DATA = {"API_KEY": "secret123", "DB_URL": "postgres://localhost/dev"}
OWNER_PASSWORD = "owner-pass"
RECIPIENT_PASSWORD = "recipient-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    create_vault(path, OWNER_PASSWORD, ENV_DATA)
    return path


def test_export_bundle_creates_file(vault_path: Path, tmp_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    assert bundle.exists()


def test_export_bundle_default_name(vault_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    assert bundle.name == "test.bundle.json"


def test_export_bundle_custom_output(vault_path: Path, tmp_path: Path) -> None:
    out = tmp_path / "custom.bundle.json"
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD, output_path=out)
    assert bundle == out
    assert out.exists()


def test_export_bundle_is_valid_json(vault_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    data = json.loads(bundle.read_text())
    assert "version" in data
    assert "payload" in data
    assert "source" in data


def test_export_bundle_version_is_1(vault_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    data = json.loads(bundle.read_text())
    assert data["version"] == 1


def test_import_bundle_roundtrip(vault_path: Path, tmp_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    dest = tmp_path / "dest.vault"
    import_bundle(bundle, RECIPIENT_PASSWORD, dest, "dest-pass")
    recovered = read_vault(dest, "dest-pass")
    assert recovered == ENV_DATA


def test_import_bundle_merges_with_existing(vault_path: Path, tmp_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    dest = tmp_path / "dest.vault"
    create_vault(dest, "dest-pass", {"EXTRA_KEY": "extra_value"})
    import_bundle(bundle, RECIPIENT_PASSWORD, dest, "dest-pass")
    recovered = read_vault(dest, "dest-pass")
    assert recovered["EXTRA_KEY"] == "extra_value"
    assert recovered["API_KEY"] == ENV_DATA["API_KEY"]


def test_import_bundle_wrong_password_raises(vault_path: Path, tmp_path: Path) -> None:
    bundle = export_bundle(vault_path, OWNER_PASSWORD, RECIPIENT_PASSWORD)
    dest = tmp_path / "dest.vault"
    with pytest.raises(ValueError):
        import_bundle(bundle, "wrong-password", dest, "dest-pass")

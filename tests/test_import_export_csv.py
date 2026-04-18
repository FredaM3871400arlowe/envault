"""Tests for CSV import/export feature."""

import csv
from pathlib import Path

import pytest

from envault.vault import create_vault, read_vault
from envault.import_export_csv import export_vault_to_csv, import_csv_to_vault, csv_preview

PASSWORD = "test-password"


@pytest.fixture()
def vault_path(tmp_path):
    path = create_vault(tmp_path / "test.vault", PASSWORD, {"KEY_A": "alpha", "KEY_B": "beta"})
    return path


def test_export_creates_csv_file(vault_path, tmp_path):
    out = tmp_path / "export.csv"
    result = export_vault_to_csv(vault_path, PASSWORD, output=out)
    assert result == out
    assert out.exists()


def test_export_default_output_name(vault_path):
    result = export_vault_to_csv(vault_path, PASSWORD)
    assert result.suffix == ".csv"
    assert result.stem == vault_path.stem


def test_export_csv_has_header_and_rows(vault_path, tmp_path):
    out = tmp_path / "export.csv"
    export_vault_to_csv(vault_path, PASSWORD, output=out)
    rows = csv_preview(out)
    keys = {r["key"] for r in rows}
    assert "KEY_A" in keys
    assert "KEY_B" in keys


def test_export_csv_values_correct(vault_path, tmp_path):
    out = tmp_path / "export.csv"
    export_vault_to_csv(vault_path, PASSWORD, output=out)
    rows = {r["key"]: r["value"] for r in csv_preview(out)}
    assert rows["KEY_A"] == "alpha"
    assert rows["KEY_B"] == "beta"


def test_import_csv_adds_keys(vault_path, tmp_path):
    csv_file = tmp_path / "new_keys.csv"
    with csv_file.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["key", "value"])
        writer.writerow(["NEW_KEY", "new_value"])
    count = import_csv_to_vault(csv_file, vault_path, PASSWORD)
    assert count == 1
    data = read_vault(vault_path, PASSWORD)
    assert data["NEW_KEY"] == "new_value"


def test_import_csv_missing_file_raises(tmp_path, vault_path):
    with pytest.raises(FileNotFoundError):
        import_csv_to_vault(tmp_path / "nope.csv", vault_path, PASSWORD)


def test_import_csv_missing_columns_raises(vault_path, tmp_path):
    bad_csv = tmp_path / "bad.csv"
    with bad_csv.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["name", "val"])
        writer.writerow(["X", "1"])
    with pytest.raises(ValueError, match="'key' and 'value'"):
        import_csv_to_vault(bad_csv, vault_path, PASSWORD)


def test_import_skips_blank_keys(vault_path, tmp_path):
    csv_file = tmp_path / "blanks.csv"
    with csv_file.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["key", "value"])
        writer.writerow(["", "ignored"])
        writer.writerow(["REAL_KEY", "real_value"])
    count = import_csv_to_vault(csv_file, vault_path, PASSWORD)
    assert count == 1

"""Tests for envault.compare."""
import pytest
from pathlib import Path
from envault.vault import create_vault, update_vault
from envault.compare import compare_vaults, compare_dicts, format_compare, CompareReport


@pytest.fixture()
def vault_a(tmp_path: Path) -> str:
    p = create_vault(str(tmp_path / "a.vault"), "passA")
    update_vault(p, "passA", {"FOO": "1", "BAR": "hello", "SHARED": "same"})
    return p


@pytest.fixture()
def vault_b(tmp_path: Path) -> str:
    p = create_vault(str(tmp_path / "b.vault"), "passB")
    update_vault(p, "passB", {"BAR": "world", "SHARED": "same", "NEW": "yes"})
    return p


def test_compare_vaults_only_in_a(vault_a, vault_b):
    report = compare_vaults(vault_a, "passA", vault_b, "passB")
    assert "FOO" in report.only_in_a


def test_compare_vaults_only_in_b(vault_a, vault_b):
    report = compare_vaults(vault_a, "passA", vault_b, "passB")
    assert "NEW" in report.only_in_b


def test_compare_vaults_changed(vault_a, vault_b):
    report = compare_vaults(vault_a, "passA", vault_b, "passB")
    keys = [k for k, _, _ in report.changed]
    assert "BAR" in keys


def test_compare_vaults_same(vault_a, vault_b):
    report = compare_vaults(vault_a, "passA", vault_b, "passB")
    assert "SHARED" in report.same


def test_has_differences_true(vault_a, vault_b):
    report = compare_vaults(vault_a, "passA", vault_b, "passB")
    assert report.has_differences is True


def test_has_differences_false():
    report = compare_dicts({"A": "1"}, {"A": "1"})
    assert report.has_differences is False


def test_format_compare_identical():
    report = CompareReport(same=["A"])
    assert format_compare(report) == "Vaults are identical."


def test_format_compare_shows_labels():
    report = CompareReport(only_in_a=["X"])
    out = format_compare(report, label_a="prod", label_b="dev")
    assert "prod" in out and "X" in out


def test_compare_dicts_changed_values():
    report = compare_dicts({"K": "old"}, {"K": "new"})
    assert report.changed == [("K", "old", "new")]

"""Tests for envault.quotas and envault.cli_quotas."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.quotas import (
    _quotas_path,
    check_quota,
    get_quota,
    list_quotas,
    load_quotas,
    remove_quota,
    set_quota,
)
from envault.cli_quotas import quotas_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


# --- unit tests ---

def test_quotas_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _quotas_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.quotas.json"


def test_load_quotas_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_quotas(vault_path) == {}


def test_set_and_get_quota(vault_path: Path) -> None:
    set_quota(vault_path, "production", 50)
    assert get_quota(vault_path, "production") == 50


def test_get_quota_missing_namespace_returns_none(vault_path: Path) -> None:
    assert get_quota(vault_path, "staging") is None


def test_set_quota_invalid_limit_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        set_quota(vault_path, "production", 0)


def test_remove_quota(vault_path: Path) -> None:
    set_quota(vault_path, "dev", 10)
    remove_quota(vault_path, "dev")
    assert get_quota(vault_path, "dev") is None


def test_remove_nonexistent_quota_is_noop(vault_path: Path) -> None:
    remove_quota(vault_path, "ghost")  # should not raise


def test_check_quota_within_limit(vault_path: Path) -> None:
    set_quota(vault_path, "ns", 5)
    assert check_quota(vault_path, "ns", 4) is True


def test_check_quota_at_limit_fails(vault_path: Path) -> None:
    set_quota(vault_path, "ns", 5)
    assert check_quota(vault_path, "ns", 5) is False


def test_check_quota_no_limit_always_passes(vault_path: Path) -> None:
    assert check_quota(vault_path, "unlimited", 999) is True


def test_list_quotas(vault_path: Path) -> None:
    set_quota(vault_path, "a", 10)
    set_quota(vault_path, "b", 20)
    result = list_quotas(vault_path)
    assert result == {"a": 10, "b": 20}


# --- CLI tests ---

def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(quotas_group, ["set", str(vault_path), "prod", "25"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "25" in result.output


def test_set_invalid_limit_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(quotas_group, ["set", str(vault_path), "prod", "0"])
    assert result.exit_code != 0


def test_get_existing_quota(runner: CliRunner, vault_path: Path) -> None:
    set_quota(vault_path, "staging", 30)
    result = runner.invoke(quotas_group, ["get", str(vault_path), "staging"])
    assert result.exit_code == 0
    assert "30" in result.output


def test_get_missing_quota(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(quotas_group, ["get", str(vault_path), "missing"])
    assert result.exit_code == 0
    assert "No quota" in result.output


def test_list_shows_all_quotas(runner: CliRunner, vault_path: Path) -> None:
    set_quota(vault_path, "alpha", 5)
    set_quota(vault_path, "beta", 15)
    result = runner.invoke(quotas_group, ["list", str(vault_path)])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_check_within_quota_exits_zero(runner: CliRunner, vault_path: Path) -> None:
    set_quota(vault_path, "ns", 10)
    result = runner.invoke(quotas_group, ["check", str(vault_path), "ns", "9"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_exceeded_quota_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    set_quota(vault_path, "ns", 10)
    result = runner.invoke(quotas_group, ["check", str(vault_path), "ns", "10"])
    assert result.exit_code != 0

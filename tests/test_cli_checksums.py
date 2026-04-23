"""Tests for envault/cli_checksums.py"""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import create_vault
from envault.checksums import record_checksum
from envault.cli_checksums import checksum_group

PASSWORD = "cli-pass"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "cv"), PASSWORD, {"MYKEY": "myval", "OTHER": "oval"})


def test_record_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        checksum_group, ["record", str(vault_path), "MYKEY", "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Checksum recorded" in result.output
    assert "MYKEY" in result.output


def test_record_unknown_key_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        checksum_group, ["record", str(vault_path), "NOPE", "--password", PASSWORD]
    )
    assert result.exit_code != 0


def test_verify_passes_for_unchanged_value(runner: CliRunner, vault_path: Path) -> None:
    record_checksum(vault_path, "MYKEY", "myval")
    result = runner.invoke(
        checksum_group, ["verify", str(vault_path), "MYKEY", "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "✓" in result.output


def test_verify_fails_for_tampered_value(runner: CliRunner, vault_path: Path) -> None:
    record_checksum(vault_path, "MYKEY", "original")
    # vault still has "myval", not "original"
    result = runner.invoke(
        checksum_group, ["verify", str(vault_path), "MYKEY", "--password", PASSWORD]
    )
    assert result.exit_code != 0
    assert "✗" in result.output


def test_verify_all_shows_each_key(runner: CliRunner, vault_path: Path) -> None:
    record_checksum(vault_path, "MYKEY", "myval")
    record_checksum(vault_path, "OTHER", "oval")
    result = runner.invoke(
        checksum_group, ["verify-all", str(vault_path), "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "MYKEY" in result.output
    assert "OTHER" in result.output


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    record_checksum(vault_path, "MYKEY", "myval")
    result = runner.invoke(checksum_group, ["remove", str(vault_path), "MYKEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_shows_recorded_keys(runner: CliRunner, vault_path: Path) -> None:
    record_checksum(vault_path, "MYKEY", "myval")
    result = runner.invoke(checksum_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "MYKEY" in result.output


def test_list_empty_message_when_none(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(checksum_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No checksums" in result.output

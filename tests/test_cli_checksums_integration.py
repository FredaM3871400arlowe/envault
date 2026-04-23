"""Integration tests for checksum CLI — record → update → verify workflow."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import create_vault, update_vault
from envault.cli_checksums import checksum_group

PASSWORD = "int-pass"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "iv"), PASSWORD, {"TOKEN": "abc123", "URL": "http://x"})


def test_record_then_verify_passes(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(checksum_group, ["record", str(vault_path), "TOKEN", "--password", PASSWORD])
    result = runner.invoke(
        checksum_group, ["verify", str(vault_path), "TOKEN", "--password", PASSWORD]
    )
    assert result.exit_code == 0


def test_record_then_update_then_verify_fails(
    runner: CliRunner, vault_path: Path
) -> None:
    runner.invoke(checksum_group, ["record", str(vault_path), "TOKEN", "--password", PASSWORD])
    update_vault(str(vault_path), PASSWORD, {"TOKEN": "changed!"})
    result = runner.invoke(
        checksum_group, ["verify", str(vault_path), "TOKEN", "--password", PASSWORD]
    )
    assert result.exit_code != 0


def test_remove_then_verify_all_excludes_key(
    runner: CliRunner, vault_path: Path
) -> None:
    runner.invoke(checksum_group, ["record", str(vault_path), "TOKEN", "--password", PASSWORD])
    runner.invoke(checksum_group, ["remove", str(vault_path), "TOKEN"])
    result = runner.invoke(
        checksum_group, ["verify-all", str(vault_path), "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "No checksums" in result.output


def test_multiple_keys_independent_checksums(
    runner: CliRunner, vault_path: Path
) -> None:
    runner.invoke(checksum_group, ["record", str(vault_path), "TOKEN", "--password", PASSWORD])
    runner.invoke(checksum_group, ["record", str(vault_path), "URL", "--password", PASSWORD])
    update_vault(str(vault_path), PASSWORD, {"URL": "http://changed"})
    result = runner.invoke(
        checksum_group, ["verify-all", str(vault_path), "--password", PASSWORD]
    )
    # TOKEN still matches, URL does not — overall exit nonzero
    assert result.exit_code != 0
    assert "TOKEN" in result.output
    assert "URL" in result.output

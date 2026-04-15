"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli import cli

PASSWORD = "test-secret"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


@pytest.fixture
def initialised_vault(runner, vault_path):
    runner.invoke(cli, ["init", vault_path, "--password", PASSWORD])
    return vault_path


def test_init_creates_vault_file(runner, vault_path):
    result = runner.invoke(cli, ["init", vault_path, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Vault created at" in result.output
    assert Path(vault_path).exists()


def test_set_and_get_key(runner, initialised_vault):
    set_result = runner.invoke(
        cli, ["set", initialised_vault, "MY_KEY", "my_value", "--password", PASSWORD]
    )
    assert set_result.exit_code == 0
    assert "Set MY_KEY" in set_result.output

    get_result = runner.invoke(
        cli, ["get", initialised_vault, "MY_KEY", "--password", PASSWORD]
    )
    assert get_result.exit_code == 0
    assert "my_value" in get_result.output


def test_get_missing_key_exits_nonzero(runner, initialised_vault):
    result = runner.invoke(
        cli, ["get", initialised_vault, "MISSING_KEY", "--password", PASSWORD]
    )
    assert result.exit_code != 0


def test_delete_key(runner, initialised_vault):
    runner.invoke(cli, ["set", initialised_vault, "DEL_KEY", "value", "--password", PASSWORD])
    del_result = runner.invoke(
        cli, ["delete", initialised_vault, "DEL_KEY", "--password", PASSWORD]
    )
    assert del_result.exit_code == 0
    assert "Deleted 'DEL_KEY'" in del_result.output

    get_result = runner.invoke(
        cli, ["get", initialised_vault, "DEL_KEY", "--password", PASSWORD]
    )
    assert get_result.exit_code != 0


def test_wrong_password_exits_nonzero(runner, initialised_vault):
    runner.invoke(cli, ["set", initialised_vault, "K", "v", "--password", PASSWORD])
    result = runner.invoke(
        cli, ["get", initialised_vault, "K", "--password", "wrong-password"]
    )
    assert result.exit_code != 0


def test_import_and_export_roundtrip(runner, initialised_vault, tmp_path):
    env_in = tmp_path / ".env"
    env_in.write_text("IMPORT_KEY=imported_value\nANOTHER=123\n")

    import_result = runner.invoke(
        cli, ["import", str(env_in), initialised_vault, "--password", PASSWORD]
    )
    assert import_result.exit_code == 0

    env_out = tmp_path / "exported.env"
    export_result = runner.invoke(
        cli, ["export", initialised_vault, str(env_out), "--password", PASSWORD]
    )
    assert export_result.exit_code == 0
    content = env_out.read_text()
    assert "IMPORT_KEY" in content
    assert "imported_value" in content

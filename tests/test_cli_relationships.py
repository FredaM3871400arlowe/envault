"""CLI tests for envault.cli_relationships."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_relationships import relationships_group
from envault.relationships import add_relationship


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_add_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(relationships_group, ["add", str(vault_path), "DB_URL", "requires", "DB_PASS"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "requires" in result.output
    assert "DB_PASS" in result.output


def test_add_invalid_type_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(relationships_group, ["add", str(vault_path), "A", "owns", "B"])
    assert result.exit_code != 0


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    add_relationship(vault_path, "A", "related", "B")
    result = runner.invoke(relationships_group, ["remove", str(vault_path), "A", "related", "B"])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_remove_unknown_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(relationships_group, ["remove", str(vault_path), "A", "related", "B"])
    assert result.exit_code != 0


def test_show_existing_relationships(runner: CliRunner, vault_path: Path) -> None:
    add_relationship(vault_path, "X", "requires", "Y")
    result = runner.invoke(relationships_group, ["show", str(vault_path), "X"])
    assert result.exit_code == 0
    assert "requires" in result.output
    assert "Y" in result.output


def test_show_no_relationships(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(relationships_group, ["show", str(vault_path), "UNKNOWN"])
    assert result.exit_code == 0
    assert "No relationships" in result.output


def test_list_shows_all(runner: CliRunner, vault_path: Path) -> None:
    add_relationship(vault_path, "A", "supersedes", "B")
    add_relationship(vault_path, "C", "conflicts", "D")
    result = runner.invoke(relationships_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "supersedes" in result.output
    assert "conflicts" in result.output


def test_list_empty_vault(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(relationships_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No relationships" in result.output


def test_types_lists_all_types(runner: CliRunner) -> None:
    result = runner.invoke(relationships_group, ["types"])
    assert result.exit_code == 0
    for rt in ("requires", "conflicts", "supersedes", "related"):
        assert rt in result.output

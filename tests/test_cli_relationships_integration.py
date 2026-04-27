"""Integration tests for key relationships feature."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_relationships import relationships_group
from envault.relationships import get_relationships, load_relationships


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "prod.vault"


def test_add_then_remove_leaves_no_trace(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(relationships_group, ["add", str(vault_path), "A", "requires", "B"])
    runner.invoke(relationships_group, ["remove", str(vault_path), "A", "requires", "B"])
    assert load_relationships(vault_path) == {}


def test_multiple_targets_same_type(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(relationships_group, ["add", str(vault_path), "API_KEY", "requires", "API_SECRET"])
    runner.invoke(relationships_group, ["add", str(vault_path), "API_KEY", "requires", "API_URL"])
    rels = get_relationships(vault_path, "API_KEY")
    assert "API_SECRET" in rels["requires"]
    assert "API_URL" in rels["requires"]


def test_remove_one_target_leaves_others(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(relationships_group, ["add", str(vault_path), "A", "related", "B"])
    runner.invoke(relationships_group, ["add", str(vault_path), "A", "related", "C"])
    runner.invoke(relationships_group, ["remove", str(vault_path), "A", "related", "B"])
    rels = get_relationships(vault_path, "A")
    assert "C" in rels["related"]
    assert "B" not in rels.get("related", [])

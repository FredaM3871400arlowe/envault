"""Tests for envault/cli_workflows.py"""
import pytest
from click.testing import CliRunner

from envault.cli_workflows import workflow_group
from envault.workflows import add_workflow


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(
        workflow_group,
        ["add", vault_path, "deploy", "--step", "echo hello", "--step", "echo world"],
    )
    assert result.exit_code == 0
    assert "deploy" in result.output
    assert "2 step" in result.output


def test_add_no_steps_exits_nonzero(runner, vault_path):
    result = runner.invoke(workflow_group, ["add", vault_path, "deploy"])
    assert result.exit_code != 0


def test_remove_prints_confirmation(runner, vault_path):
    add_workflow(vault_path, "ci", ["pytest"])
    result = runner.invoke(workflow_group, ["remove", vault_path, "ci"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_exits_nonzero(runner, vault_path):
    result = runner.invoke(workflow_group, ["remove", vault_path, "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_list_shows_workflows(runner, vault_path):
    add_workflow(vault_path, "build", ["make"])
    add_workflow(vault_path, "test", ["pytest"])
    result = runner.invoke(workflow_group, ["list", vault_path])
    assert result.exit_code == 0
    assert "build" in result.output
    assert "test" in result.output


def test_list_empty_vault(runner, vault_path):
    result = runner.invoke(workflow_group, ["list", vault_path])
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_show_displays_steps(runner, vault_path):
    add_workflow(vault_path, "deploy", ["step_a", "step_b"], description="Deploy app")
    result = runner.invoke(workflow_group, ["show", vault_path, "deploy"])
    assert result.exit_code == 0
    assert "step_a" in result.output
    assert "step_b" in result.output
    assert "Deploy app" in result.output


def test_show_unknown_exits_nonzero(runner, vault_path):
    result = runner.invoke(workflow_group, ["show", vault_path, "ghost"])
    assert result.exit_code != 0

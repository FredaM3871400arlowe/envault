"""Tests for envault/workflows.py"""
import pytest

from envault.workflows import (
    _workflows_path,
    add_workflow,
    get_workflow,
    list_workflows,
    load_workflows,
    remove_workflow,
)


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_workflows_path_is_sibling_of_vault(vault_path):
    p = _workflows_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.workflows.json"


def test_load_workflows_returns_empty_when_missing(vault_path):
    assert load_workflows(vault_path) == {}


def test_add_workflow_creates_entry(vault_path):
    add_workflow(vault_path, "deploy", ["envault get DB_URL", "./deploy.sh"])
    data = load_workflows(vault_path)
    assert "deploy" in data
    assert data["deploy"]["steps"] == ["envault get DB_URL", "./deploy.sh"]


def test_add_workflow_stores_description(vault_path):
    add_workflow(vault_path, "build", ["make"], description="Build the project")
    wf = get_workflow(vault_path, "build")
    assert wf["description"] == "Build the project"


def test_add_workflow_empty_name_raises(vault_path):
    with pytest.raises(ValueError, match="name"):
        add_workflow(vault_path, "", ["echo hi"])


def test_add_workflow_empty_steps_raises(vault_path):
    with pytest.raises(ValueError, match="step"):
        add_workflow(vault_path, "empty", [])


def test_get_workflow_missing_key_returns_none(vault_path):
    assert get_workflow(vault_path, "nonexistent") is None


def test_remove_workflow_deletes_entry(vault_path):
    add_workflow(vault_path, "ci", ["pytest"])
    remove_workflow(vault_path, "ci")
    assert get_workflow(vault_path, "ci") is None


def test_remove_workflow_unknown_raises(vault_path):
    with pytest.raises(KeyError):
        remove_workflow(vault_path, "ghost")


def test_list_workflows_returns_sorted_names(vault_path):
    add_workflow(vault_path, "zebra", ["z"])
    add_workflow(vault_path, "alpha", ["a"])
    assert list_workflows(vault_path) == ["alpha", "zebra"]


def test_add_workflow_overwrites_existing(vault_path):
    add_workflow(vault_path, "deploy", ["step1"])
    add_workflow(vault_path, "deploy", ["step2", "step3"])
    wf = get_workflow(vault_path, "deploy")
    assert wf["steps"] == ["step2", "step3"]

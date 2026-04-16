"""Tests for envault/cli_templates.py."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_templates import template_group
from envault.templates import add_template


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    p.write_bytes(b"")
    return str(p)


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(
        template_group, ["add", "backend", "DB_URL", "SECRET", "--vault", vault_path]
    )
    assert result.exit_code == 0
    assert "backend" in result.output
    assert "2 key(s)" in result.output


def test_remove_prints_confirmation(runner, vault_path, tmp_path):
    add_template(tmp_path, "svc", ["A"])
    result = runner.invoke(
        template_group, ["remove", "svc", "--vault", vault_path]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_shows_error(runner, vault_path):
    result = runner.invoke(
        template_group, ["remove", "ghost", "--vault", vault_path]
    )
    assert "Error" in result.output


def test_list_shows_templates(runner, vault_path, tmp_path):
    add_template(tmp_path, "alpha", ["KEY1", "KEY2"])
    result = runner.invoke(template_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0


def test_list_empty(runner, vault_path):
    result = runner.invoke(template_group, ["list", "--vault", vault_path])
    assert "No templates" in result.output


def test_show_template_keys(runner, vault_path, tmp_path):
    add_template(tmp_path, "mytemplate", ["FOO", "BAR"])
    result = runner.invoke(
        template_group, ["show", "mytemplate", "--vault", vault_path]
    )
    assert result.exit_code == 0


def test_show_unknown_template_error(runner, vault_path):
    result = runner.invoke(
        template_group, ["show", "nope", "--vault", vault_path]
    )
    assert "Error" in result.output

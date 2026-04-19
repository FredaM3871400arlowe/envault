"""Integration tests: bookmarks survive multiple CLI invocations."""
import pytest
from click.testing import CliRunner
from envault.cli_bookmarks import bookmarks_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_bookmark_persists_after_second_add(runner, vault_path):
    runner.invoke(bookmarks_group, ["add", "x", "KEY_X", "--vault", vault_path])
    runner.invoke(bookmarks_group, ["add", "y", "KEY_Y", "--vault", vault_path])
    result = runner.invoke(bookmarks_group, ["list", "--vault", vault_path])
    assert "x -> KEY_X" in result.output
    assert "y -> KEY_Y" in result.output


def test_remove_does_not_affect_other_bookmarks(runner, vault_path):
    runner.invoke(bookmarks_group, ["add", "a", "KEY_A", "--vault", vault_path])
    runner.invoke(bookmarks_group, ["add", "b", "KEY_B", "--vault", vault_path])
    runner.invoke(bookmarks_group, ["remove", "a", "--vault", vault_path])
    result = runner.invoke(bookmarks_group, ["list", "--vault", vault_path])
    assert "a" not in result.output
    assert "b -> KEY_B" in result.output


def test_overwrite_bookmark_via_add(runner, vault_path):
    runner.invoke(bookmarks_group, ["add", "db", "OLD_KEY", "--vault", vault_path])
    runner.invoke(bookmarks_group, ["add", "db", "NEW_KEY", "--vault", vault_path])
    result = runner.invoke(bookmarks_group, ["resolve", "db", "--vault", vault_path])
    assert "NEW_KEY" in result.output
    assert "OLD_KEY" not in result.output

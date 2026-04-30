import pytest
from click.testing import CliRunner
from envault.cli_bookmarks import bookmarks_group
from envault.bookmarks import add_bookmark


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(bookmarks_group, ["add", "db", "DATABASE_URL", "--vault", vault_path])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DATABASE_URL" in result.output


def test_add_duplicate_shows_error(runner, vault_path):
    add_bookmark(vault_path, "db", "DATABASE_URL")
    result = runner.invoke(bookmarks_group, ["add", "db", "OTHER_URL", "--vault", vault_path])
    assert result.exit_code != 0


def test_remove_prints_confirmation(runner, vault_path):
    add_bookmark(vault_path, "db", "DATABASE_URL")
    result = runner.invoke(bookmarks_group, ["remove", "db", "--vault", vault_path])
    assert result.exit_code == 0
    assert "db" in result.output


def test_remove_unknown_shows_error(runner, vault_path):
    result = runner.invoke(bookmarks_group, ["remove", "ghost", "--vault", vault_path])
    assert result.exit_code != 0


def test_resolve_shows_key(runner, vault_path):
    add_bookmark(vault_path, "sec", "SECRET_KEY")
    result = runner.invoke(bookmarks_group, ["resolve", "sec", "--vault", vault_path])
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.output


def test_resolve_unknown_shows_error(runner, vault_path):
    result = runner.invoke(bookmarks_group, ["resolve", "ghost", "--vault", vault_path])
    assert result.exit_code != 0


def test_list_shows_all(runner, vault_path):
    add_bookmark(vault_path, "a", "KEY_A")
    add_bookmark(vault_path, "b", "KEY_B")
    result = runner.invoke(bookmarks_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "a -> KEY_A" in result.output
    assert "b -> KEY_B" in result.output


def test_list_empty_shows_message(runner, vault_path):
    result = runner.invoke(bookmarks_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "No bookmarks" in result.output

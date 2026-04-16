"""Integration tests: tags interact correctly with vault keys."""
import pytest
from click.testing import CliRunner
from envault.vault import create_vault, update_vault
from envault.tags import add_tag, keys_with_tag, get_tags
from envault.cli_tags import tags_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def populated_vault(tmp_path):
    path = create_vault(tmp_path / "env.vault", "secret")
    update_vault(path, "secret", {"DB_HOST": "localhost", "API_KEY": "abc123", "REDIS_URL": "redis://"})
    return path


def test_tag_survives_vault_update(populated_vault):
    add_tag(populated_vault, "DB_HOST", "infra")
    update_vault(populated_vault, "secret", {"DB_HOST": "prod-db"})
    assert "infra" in get_tags(populated_vault, "DB_HOST")


def test_multiple_keys_same_tag_find(populated_vault):
    add_tag(populated_vault, "DB_HOST", "prod")
    add_tag(populated_vault, "REDIS_URL", "prod")
    result = keys_with_tag(populated_vault, "prod")
    assert "DB_HOST" in result
    assert "REDIS_URL" in result


def test_cli_find_no_match(runner, populated_vault):
    result = runner.invoke(tags_group, ["find", str(populated_vault), "nonexistent"])
    assert "No keys" in result.output
    assert result.exit_code == 0


def test_tags_are_independent_per_vault(tmp_path):
    v1 = create_vault(tmp_path / "v1.vault", "p")
    v2 = create_vault(tmp_path / "v2.vault", "p")
    add_tag(v1, "KEY", "shared")
    assert keys_with_tag(v2, "shared") == []

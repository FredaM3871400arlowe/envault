"""Tests for envault.search."""

import pytest

from envault.vault import create_vault, update_vault
from envault.search import search_vault, format_results, SearchResult


@pytest.fixture()
def vault_path(tmp_path):
    path = create_vault(str(tmp_path / "test.vault"), "pass")
    update_vault(path, "pass", {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret123", "APP_ENV": "production"})
    return path


def test_search_by_key_prefix(vault_path):
    results = search_vault(vault_path, "pass", "DB_", search_keys=True)
    keys = {r.key for r in results}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_search_by_key_case_insensitive(vault_path):
    results = search_vault(vault_path, "pass", "db_host", search_keys=True)
    assert any(r.key == "DB_HOST" for r in results)


def test_search_by_key_case_sensitive_no_match(vault_path):
    results = search_vault(vault_path, "pass", "db_host", search_keys=True, case_sensitive=True)
    assert results == []


def test_search_by_value(vault_path):
    results = search_vault(vault_path, "pass", "localhost", search_keys=False, search_values=True)
    assert len(results) == 1
    assert results[0].key == "DB_HOST"
    assert results[0].matched_on == "value"


def test_search_matched_on_both(vault_path):
    # pattern matches key name and value for APP_ENV
    results = search_vault(vault_path, "pass", "production", search_keys=True, search_values=True)
    assert results[0].matched_on == "value"


def test_search_no_results(vault_path):
    results = search_vault(vault_path, "pass", "NONEXISTENT")
    assert results == []


def test_search_invalid_pattern_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid pattern"):
        search_vault(vault_path, "pass", "[unclosed")


def test_search_wrong_password_raises(vault_path):
    with pytest.raises(ValueError):
        search_vault(vault_path, "wrong", "DB")


def test_format_results_empty():
    assert format_results([]) == "No matches found."


def test_format_results_shows_keys():
    results = [SearchResult(key="DB_HOST", value="localhost", matched_on="key")]
    output = format_results(results)
    assert "DB_HOST" in output
    assert "localhost" not in output


def test_format_results_show_values():
    results = [SearchResult(key="DB_HOST", value="localhost", matched_on="key")]
    output = format_results(results, show_values=True)
    assert "localhost" in output

"""Tests for envault.trends and envault.cli_trends."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.trends import (
    _trends_path,
    clear_trends,
    get_change_count,
    get_most_changed,
    load_trends,
    record_change,
)
from envault.cli_trends import trends_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_trends_path_is_sibling_of_vault(vault_path: Path) -> None:
    assert _trends_path(vault_path) == vault_path.with_suffix(".trends.json")


def test_load_trends_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_trends(vault_path) == {}


def test_record_change_creates_entry(vault_path: Path) -> None:
    ts = record_change(vault_path, "DB_URL")
    data = load_trends(vault_path)
    assert "DB_URL" in data
    assert ts in data["DB_URL"]


def test_record_change_appends(vault_path: Path) -> None:
    record_change(vault_path, "SECRET")
    record_change(vault_path, "SECRET")
    assert get_change_count(vault_path, "SECRET") == 2


def test_get_change_count_missing_key_returns_zero(vault_path: Path) -> None:
    assert get_change_count(vault_path, "MISSING") == 0


def test_get_most_changed_ordering(vault_path: Path) -> None:
    for _ in range(3):
        record_change(vault_path, "A")
    for _ in range(5):
        record_change(vault_path, "B")
    record_change(vault_path, "C")
    top = get_most_changed(vault_path, top_n=2)
    assert top[0] == ("B", 5)
    assert top[1] == ("A", 3)


def test_get_most_changed_respects_top_n(vault_path: Path) -> None:
    for key in ("X", "Y", "Z"):
        record_change(vault_path, key)
    assert len(get_most_changed(vault_path, top_n=2)) == 2


def test_clear_trends_removes_key(vault_path: Path) -> None:
    record_change(vault_path, "TOKEN")
    assert clear_trends(vault_path, "TOKEN") is True
    assert load_trends(vault_path) == {}


def test_clear_trends_missing_key_returns_false(vault_path: Path) -> None:
    assert clear_trends(vault_path, "NOPE") is False


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_record_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(trends_group, ["record", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "Recorded change for 'API_KEY'" in result.output


def test_count_shows_correct_number(runner: CliRunner, vault_path: Path) -> None:
    record_change(vault_path, "MY_KEY")
    record_change(vault_path, "MY_KEY")
    result = runner.invoke(trends_group, ["count", str(vault_path), "MY_KEY"])
    assert result.exit_code == 0
    assert "2 time(s)" in result.output


def test_top_shows_ranked_keys(runner: CliRunner, vault_path: Path) -> None:
    for _ in range(4):
        record_change(vault_path, "ALPHA")
    record_change(vault_path, "BETA")
    result = runner.invoke(trends_group, ["top", str(vault_path), "--n", "2"])
    assert result.exit_code == 0
    assert "ALPHA" in result.output


def test_list_shows_all_keys(runner: CliRunner, vault_path: Path) -> None:
    record_change(vault_path, "K1")
    record_change(vault_path, "K2")
    result = runner.invoke(trends_group, ["list", str(vault_path)])
    assert "K1" in result.output
    assert "K2" in result.output


def test_clear_unknown_key_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(trends_group, ["clear", str(vault_path), "GHOST"])
    assert result.exit_code != 0

"""Tests for envault.cli_profiles CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_profiles import profile_group
from envault.profiles import add_profile


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_add_prints_confirmation(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(profile_group, ["add", "dev", "dev.vault"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "dev.vault" in result.output


def test_remove_prints_confirmation(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path) as iso:
        add_profile("dev", "dev.vault", Path(iso))
        result = runner.invoke(profile_group, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_profile_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(profile_group, ["remove", "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_list_shows_all_profiles(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path) as iso:
        base = Path(iso)
        add_profile("dev", "dev.vault", base)
        add_profile("prod", "prod.vault", base)
        result = runner.invoke(profile_group, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_empty_message_when_no_profiles(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(profile_group, ["list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_show_displays_vault_path(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path) as iso:
        add_profile("staging", "staging.vault", Path(iso))
        result = runner.invoke(profile_group, ["show", "staging"])
    assert result.exit_code == 0
    assert "staging.vault" in result.output


def test_show_unknown_profile_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(profile_group, ["show", "nope"])
    assert result.exit_code != 0
    assert "nope" in result.output

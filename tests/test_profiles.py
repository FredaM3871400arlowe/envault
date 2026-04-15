"""Tests for envault.profiles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.profiles import (
    _profiles_path,
    add_profile,
    get_profile,
    list_profiles,
    load_profiles,
    remove_profile,
    save_profiles,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_profiles_path_is_in_base_dir(base: Path) -> None:
    path = _profiles_path(base)
    assert path.parent == base
    assert path.name == ".envault_profiles.json"


def test_load_profiles_returns_empty_dict_when_missing(base: Path) -> None:
    assert load_profiles(base) == {}


def test_save_and_load_roundtrip(base: Path) -> None:
    data = {"dev": {"vault": "dev.vault"}}
    save_profiles(data, base)
    assert load_profiles(base) == data


def test_add_profile_creates_entry(base: Path) -> None:
    profiles = add_profile("dev", "dev.vault", base)
    assert "dev" in profiles
    assert profiles["dev"]["vault"] == "dev.vault"


def test_add_profile_overwrites_existing(base: Path) -> None:
    add_profile("dev", "old.vault", base)
    add_profile("dev", "new.vault", base)
    assert get_profile("dev", base)["vault"] == "new.vault"


def test_add_profile_persists_to_disk(base: Path) -> None:
    add_profile("prod", "prod.vault", base)
    raw = json.loads(_profiles_path(base).read_text())
    assert "prod" in raw


def test_remove_profile_deletes_entry(base: Path) -> None:
    add_profile("staging", "staging.vault", base)
    remove_profile("staging", base)
    assert "staging" not in load_profiles(base)


def test_remove_profile_raises_for_unknown(base: Path) -> None:
    with pytest.raises(KeyError, match="ghost"):
        remove_profile("ghost", base)


def test_get_profile_returns_correct_data(base: Path) -> None:
    add_profile("ci", "ci.vault", base)
    info = get_profile("ci", base)
    assert info["vault"] == "ci.vault"


def test_get_profile_raises_for_unknown(base: Path) -> None:
    with pytest.raises(KeyError):
        get_profile("missing", base)


def test_list_profiles_returns_sorted_names(base: Path) -> None:
    add_profile("prod", "p.vault", base)
    add_profile("dev", "d.vault", base)
    add_profile("staging", "s.vault", base)
    assert list_profiles(base) == ["dev", "prod", "staging"]


def test_list_profiles_empty_when_no_profiles(base: Path) -> None:
    assert list_profiles(base) == []

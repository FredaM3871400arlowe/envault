"""Tests for envault/templates.py."""

from __future__ import annotations

import pytest

from envault.templates import (
    _templates_path,
    add_template,
    remove_template,
    get_template,
    load_templates,
    save_templates,
    apply_template,
)


@pytest.fixture()
def base(tmp_path):
    return tmp_path


def test_templates_path_is_in_base_dir(base):
    p = _templates_path(base)
    assert p.parent == base
    assert p.name == ".envault_templates.json"


def test_load_templates_returns_empty_when_missing(base):
    assert load_templates(base) == {}


def test_add_template_creates_entry(base):
    add_template(base, "backend", ["DB_URL", "SECRET_KEY"])
    templates = load_templates(base)
    assert "backend" in templates
    assert templates["backend"] == ["DB_URL", "SECRET_KEY"]


def test_add_template_empty_keys_raises(base):
    with pytest.raises(ValueError):
        add_template(base, "empty", [])


def test_add_template_overwrites_existing(base):
    add_template(base, "svc", ["A"])
    add_template(base, "svc", ["B", "C"])
    assert get_template(base, "svc") == ["B", "C"]


def test_remove_template(base):
    add_template(base, "tpl", ["X"])
    remove_template(base, "tpl")
    assert "tpl" not in load_templates(base)


def test_remove_unknown_template_raises(base):
    with pytest.raises(KeyError):
        remove_template(base, "nonexistent")


def test_get_template_unknown_raises(base):
    with pytest.raises(KeyError):
        get_template(base, "ghost")


def test_save_and_load_roundtrip(base):
    data = {"t1": ["A", "B"], "t2": ["C"]}
    save_templates(base, data)
    assert load_templates(base) == data


def test_apply_template_filters_keys(base):
    vault_data = {"DB_URL": "postgres://", "SECRET": "abc", "PORT": "5432"}
    result = apply_template(vault_data, ["DB_URL", "PORT", "MISSING"])
    assert result == {"DB_URL": "postgres://", "PORT": "5432"}


def test_apply_template_empty_keys(base):
    assert apply_template({"A": "1"}, []) == {}

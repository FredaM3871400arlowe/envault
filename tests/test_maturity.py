"""Tests for envault.maturity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.maturity import (
    MaturityResult,
    _classify,
    compute_maturity,
    get_maturity,
    load_maturity,
    _maturity_path,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, {"KEY_A": "alpha", "KEY_B": "beta"}, "secret")
    return p


def _ts(days_ago: float) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def test_maturity_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _maturity_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.maturity.json"


def test_load_maturity_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_maturity(vault_path) == {}


def test_classify_new() -> None:
    assert _classify(0.5, 0) == "new"


def test_classify_developing() -> None:
    assert _classify(5, 3) == "developing"


def test_classify_stable() -> None:
    assert _classify(20, 5) == "stable"


def test_classify_mature() -> None:
    assert _classify(60, 12) == "mature"


def test_classify_stale() -> None:
    assert _classify(100, 1) == "stale"


def test_compute_maturity_creates_file(vault_path: Path) -> None:
    compute_maturity(vault_path, ["KEY_A", "KEY_B"])
    assert _maturity_path(vault_path).exists()


def test_compute_maturity_returns_results(vault_path: Path) -> None:
    results = compute_maturity(vault_path, ["KEY_A"])
    assert "KEY_A" in results
    r = results["KEY_A"]
    assert isinstance(r, MaturityResult)
    assert r.level == "new"
    assert r.age_days == 0.0


def test_compute_maturity_with_history(vault_path: Path) -> None:
    history = {
        "KEY_A": [
            {"timestamp": _ts(60)},
            *[{"timestamp": _ts(60 - i)} for i in range(1, 12)],
        ]
    }
    results = compute_maturity(vault_path, ["KEY_A"], history=history)
    assert results["KEY_A"].level == "mature"


def test_get_maturity_returns_none_when_missing(vault_path: Path) -> None:
    assert get_maturity(vault_path, "MISSING") is None


def test_get_maturity_returns_result_after_compute(vault_path: Path) -> None:
    compute_maturity(vault_path, ["KEY_B"])
    r = get_maturity(vault_path, "KEY_B")
    assert r is not None
    assert r.key == "KEY_B"


def test_compute_maturity_persists_all_keys(vault_path: Path) -> None:
    compute_maturity(vault_path, ["KEY_A", "KEY_B"])
    data = load_maturity(vault_path)
    assert set(data.keys()) == {"KEY_A", "KEY_B"}

"""Tests for envault.projections."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.projections import (
    ProjectionResult,
    _projections_path,
    compute_projections,
    load_projections,
)
from envault.trends import save_trends
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "password")


def _make_entries(n: int, span_days: float = 10.0) -> list:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    step = timedelta(days=span_days / max(n - 1, 1))
    return [
        {"timestamp": (base + step * i).isoformat(), "action": "set"}
        for i in range(n)
    ]


def test_projections_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _projections_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == vault_path.stem + ".projections.json"


def test_load_projections_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_projections(vault_path) == {}


def test_compute_projections_returns_projection_result(vault_path: Path) -> None:
    entries = _make_entries(11, span_days=10.0)
    save_trends(vault_path, {"API_KEY": entries})
    results = compute_projections(vault_path)
    assert "API_KEY" in results
    r = results["API_KEY"]
    assert isinstance(r, ProjectionResult)
    assert r.key == "API_KEY"
    assert r.total_changes == 11


def test_compute_projections_persists_to_file(vault_path: Path) -> None:
    save_trends(vault_path, {"DB_PASS": _make_entries(5, 4.0)})
    compute_projections(vault_path)
    data = load_projections(vault_path)
    assert "DB_PASS" in data
    assert "projected_changes_30d" in data["DB_PASS"]


def test_compute_projections_no_entries_returns_zeros(vault_path: Path) -> None:
    save_trends(vault_path, {"EMPTY_KEY": []})
    results = compute_projections(vault_path)
    r = results["EMPTY_KEY"]
    assert r.total_changes == 0
    assert r.avg_changes_per_day == 0.0
    assert r.projected_changes_30d == 0.0


def test_compute_projections_single_entry(vault_path: Path) -> None:
    save_trends(vault_path, {"SOLO": [{"timestamp": "2024-06-01T00:00:00+00:00", "action": "set"}]})
    results = compute_projections(vault_path)
    r = results["SOLO"]
    assert r.total_changes == 1
    assert r.avg_changes_per_day == 1.0
    assert r.projected_changes_30d == 30.0


def test_compute_projections_filters_to_requested_keys(vault_path: Path) -> None:
    save_trends(vault_path, {
        "KEY_A": _make_entries(3),
        "KEY_B": _make_entries(7),
    })
    results = compute_projections(vault_path, keys=["KEY_A"])
    assert "KEY_A" in results
    assert "KEY_B" not in results


def test_projected_90d_is_three_times_30d(vault_path: Path) -> None:
    save_trends(vault_path, {"TOKEN": _make_entries(10, 9.0)})
    results = compute_projections(vault_path)
    r = results["TOKEN"]
    assert abs(r.projected_changes_90d - r.projected_changes_30d * 3) < 0.01

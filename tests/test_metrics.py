"""Tests for envault.metrics."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.vault import create_vault, update_vault
from envault.metrics import (
    _metrics_path,
    compute_metrics,
    format_metrics,
    load_metrics,
    record_metrics,
)

PASSWORD = "test-secret"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = create_vault(tmp_path / "test.vault", PASSWORD)
    update_vault(p, PASSWORD, {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": ""})
    return p


def test_metrics_path_is_sibling_of_vault(vault_path: Path) -> None:
    mp = _metrics_path(vault_path)
    assert mp.parent == vault_path.parent
    assert mp.name == "test.metrics.json"


def test_compute_metrics_total_keys(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    assert m.total_keys == 3


def test_compute_metrics_empty_values(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    assert m.empty_values == 1


def test_compute_metrics_avg_value_length(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    # "localhost" = 9, "5432" = 4, "" = 0  -> avg = 13/3 ≈ 4.33
    assert m.avg_value_length == round((9 + 4 + 0) / 3, 2)


def test_compute_metrics_longest_key(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    assert m.longest_key == "DB_HOST"


def test_compute_metrics_shortest_key(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    assert m.shortest_key == "SECRET"


def test_compute_metrics_empty_vault(tmp_path: Path) -> None:
    p = create_vault(tmp_path / "empty.vault", PASSWORD)
    m = compute_metrics(p, PASSWORD)
    assert m.total_keys == 0
    assert m.longest_key == ""
    assert m.shortest_key == ""
    assert m.avg_value_length == 0.0


def test_record_metrics_creates_file(vault_path: Path) -> None:
    record_metrics(vault_path, PASSWORD)
    assert _metrics_path(vault_path).exists()


def test_record_metrics_persists_correctly(vault_path: Path) -> None:
    record_metrics(vault_path, PASSWORD)
    data = load_metrics(vault_path)
    assert data["total_keys"] == 3
    assert data["empty_values"] == 1
    assert "avg_value_length" in data


def test_load_metrics_returns_empty_when_missing(tmp_path: Path) -> None:
    p = tmp_path / "ghost.vault"
    assert load_metrics(p) == {}


def test_format_metrics_contains_labels(vault_path: Path) -> None:
    m = compute_metrics(vault_path, PASSWORD)
    output = format_metrics(m)
    assert "Total keys" in output
    assert "Empty values" in output
    assert "Avg value length" in output
    assert "Longest key" in output
    assert "Shortest key" in output

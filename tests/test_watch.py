"""Tests for envault.watch."""
from __future__ import annotations

import time
import threading
from pathlib import Path

import pytest

from envault.vault import create_vault, read_vault
from envault.watch import watch_env_file

PASSWORD = "watchpass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "watch.vault"
    create_vault(p, PASSWORD, {"INITIAL": "yes"})
    return p


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("FOO=bar\n")
    return p


def test_watch_syncs_on_change(vault_path: Path, env_file: Path) -> None:
    synced: list[Path] = []

    def run() -> None:
        watch_env_file(
            env_file,
            vault_path,
            PASSWORD,
            interval=0.05,
            on_sync=synced.append,
            stop_after=1,
        )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(0.1)
    env_file.write_text("FOO=changed\nBAR=new\n")
    t.join(timeout=3)

    assert len(synced) == 1
    data = read_vault(vault_path, PASSWORD)
    assert data["FOO"] == "changed"
    assert data["BAR"] == "new"


def test_watch_no_sync_when_file_unchanged(vault_path: Path, env_file: Path) -> None:
    synced: list[Path] = []

    def run() -> None:
        watch_env_file(
            env_file,
            vault_path,
            PASSWORD,
            interval=0.05,
            on_sync=synced.append,
            stop_after=1,
        )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout=0.5)
    assert len(synced) == 0


def test_watch_raises_if_env_missing(vault_path: Path, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        watch_env_file(tmp_path / "missing.env", vault_path, PASSWORD, stop_after=1)

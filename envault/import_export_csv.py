"""CSV import/export support for envault vaults."""

from __future__ import annotations

import csv
import io
from pathlib import Path

from envault.vault import read_vault, update_vault


def export_vault_to_csv(vault_path: str | Path, password: str, output: str | Path | None = None) -> Path:
    """Export all key/value pairs from a vault to a CSV file."""
    vault_path = Path(vault_path)
    data = read_vault(vault_path, password)

    if output is None:
        output = vault_path.with_suffix(".csv")
    output = Path(output)

    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["key", "value"])
        for key, value in sorted(data.items()):
            writer.writerow([key, value])

    return output


def import_csv_to_vault(csv_path: str | Path, vault_path: str | Path, password: str) -> int:
    """Import key/value pairs from a CSV file into an existing vault.

    The CSV must have 'key' and 'value' columns (header row required).
    Returns the number of keys imported.
    """
    csv_path = Path(csv_path)
    vault_path = Path(vault_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or "key" not in reader.fieldnames or "value" not in reader.fieldnames:
            raise ValueError("CSV must contain 'key' and 'value' columns")
        rows = list(reader)

    count = 0
    for row in rows:
        key = row["key"].strip()
        value = row["value"]
        if not key:
            continue
        update_vault(vault_path, password, key, value)
        count += 1

    return count


def csv_preview(csv_path: str | Path) -> list[dict[str, str]]:
    """Return parsed rows from a CSV without touching any vault."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]

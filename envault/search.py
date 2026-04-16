"""Search keys across a vault by name or value pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from envault.vault import read_vault


@dataclass
class SearchResult:
    key: str
    value: str
    matched_on: str  # 'key' | 'value' | 'both'


def search_vault(
    vault_path: str,
    password: str,
    pattern: str,
    *,
    search_keys: bool = True,
    search_values: bool = False,
    case_sensitive: bool = False,
) -> list[SearchResult]:
    """Return all entries whose key and/or value match *pattern*."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid pattern: {exc}") from exc

    data = read_vault(vault_path, password)
    results: list[SearchResult] = []

    for key, value in data.items():
        key_match = search_keys and bool(regex.search(key))
        val_match = search_values and bool(regex.search(value))

        if key_match and val_match:
            matched_on = "both"
        elif key_match:
            matched_on = "key"
        elif val_match:
            matched_on = "value"
        else:
            continue

        results.append(SearchResult(key=key, value=value, matched_on=matched_on))

    return results


def format_results(results: list[SearchResult], *, show_values: bool = False) -> str:
    """Render search results as a human-readable string."""
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        val_part = f" = {r.value}" if show_values else ""
        lines.append(f"  [{r.matched_on}] {r.key}{val_part}")
    return "\n".join(lines)

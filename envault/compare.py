"""Compare two vaults side-by-side."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envault.vault import read_vault


@dataclass
class CompareReport:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # key, val_a, val_b
    same: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.changed)


def compare_vaults(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: str,
) -> CompareReport:
    data_a: Dict[str, str] = read_vault(vault_a, password_a)
    data_b: Dict[str, str] = read_vault(vault_b, password_b)
    return compare_dicts(data_a, data_b)


def compare_dicts(a: Dict[str, str], b: Dict[str, str]) -> CompareReport:
    report = CompareReport()
    all_keys = set(a) | set(b)
    for key in sorted(all_keys):
        in_a, in_b = key in a, key in b
        if in_a and not in_b:
            report.only_in_a.append(key)
        elif in_b and not in_a:
            report.only_in_b.append(key)
        elif a[key] == b[key]:
            report.same.append(key)
        else:
            report.changed.append((key, a[key], b[key]))
    return report


def format_compare(report: CompareReport, label_a: str = "A", label_b: str = "B") -> str:
    lines: List[str] = []
    for key in report.only_in_a:
        lines.append(f"  only in {label_a}: {key}")
    for key in report.only_in_b:
        lines.append(f"  only in {label_b}: {key}")
    for key, va, vb in report.changed:
        lines.append(f"  changed : {key}")
        lines.append(f"    {label_a}: {va}")
        lines.append(f"    {label_b}: {vb}")
    if not lines:
        return "Vaults are identical."
    return "\n".join(lines)

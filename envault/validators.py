"""Key/value validation rules for vault entries."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
import re


@dataclass
class ValidationIssue:
    key: str
    message: str


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def add(self, key: str, message: str) -> None:
        self.issues.append(ValidationIssue(key=key, message=message))


Rule = Callable[[str, str], str | None]

_BUILTIN_RULES: list[tuple[str, Rule]] = []


def rule(name: str):
    def decorator(fn: Rule):
        _BUILTIN_RULES.append((name, fn))
        return fn
    return decorator


@rule("no_empty_value")
def _no_empty_value(key: str, value: str) -> str | None:
    if value.strip() == "":
        return "Value is empty."
    return None


@rule("no_whitespace_in_key")
def _no_whitespace_in_key(key: str, value: str) -> str | None:
    if re.search(r"\s", key):
        return "Key contains whitespace."
    return None


@rule("key_uppercase")
def _key_uppercase(key: str, value: str) -> str | None:
    if key != key.upper():
        return "Key is not uppercase."
    return None


@rule("no_placeholder_value")
def _no_placeholder(key: str, value: str) -> str | None:
    placeholders = {"changeme", "todo", "fixme", "your_value", "xxx"}
    if value.strip().lower() in placeholders:
        return f"Value looks like a placeholder: '{value}'."
    return None


def validate_dict(
    data: dict[str, str],
    extra_rules: list[Rule] | None = None,
) -> ValidationReport:
    report = ValidationReport()
    rules = [fn for _, fn in _BUILTIN_RULES] + (extra_rules or [])
    for key, value in data.items():
        for fn in rules:
            msg = fn(key, value)
            if msg:
                report.add(key, msg)
    return report


def format_report(report: ValidationReport) -> str:
    if report.ok:
        return "All keys passed validation."
    lines = ["Validation issues:"]
    for issue in report.issues:
        lines.append(f"  [{issue.key}] {issue.message}")
    return "\n".join(lines)

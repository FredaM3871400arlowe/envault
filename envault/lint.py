"""Lint vault keys against a set of rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import read_vault


@dataclass
class LintIssue:
    key: str
    rule: str
    message: str


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def add(self, key: str, rule: str, message: str) -> None:
        self.issues.append(LintIssue(key=key, rule=rule, message=message))


_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')


def _check_naming(key: str, report: LintReport) -> None:
    if not _KEY_RE.match(key):
        report.add(key, "naming", f"Key '{key}' should be UPPER_SNAKE_CASE")


def _check_empty_value(key: str, value: str, report: LintReport) -> None:
    if value.strip() == "":
        report.add(key, "empty_value", f"Key '{key}' has an empty value")


def _check_placeholder(key: str, value: str, report: LintReport) -> None:
    placeholders = {"changeme", "todo", "fixme", "placeholder", "xxx", "your_value_here"}
    if value.strip().lower() in placeholders:
        report.add(key, "placeholder", f"Key '{key}' appears to contain a placeholder value")


def lint_dict(env: Dict[str, str]) -> LintReport:
    report = LintReport()
    for key, value in env.items():
        _check_naming(key, report)
        _check_empty_value(key, value, report)
        _check_placeholder(key, value, report)
    return report


def lint_vault(vault_path: str, password: str) -> LintReport:
    env = read_vault(vault_path, password)
    return lint_dict(env)


def format_report(report: LintReport) -> str:
    if report.ok:
        return "No issues found."
    lines = [f"Found {len(report.issues)} issue(s):"]
    for issue in report.issues:
        lines.append(f"  [{issue.rule}] {issue.message}")
    return "\n".join(lines)

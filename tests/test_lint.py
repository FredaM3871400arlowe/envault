"""Tests for envault.lint."""
import pytest
from pathlib import Path

from envault.vault import create_vault, update_vault
from envault.lint import lint_dict, lint_vault, format_report, LintReport


PASSWORD = "lintpass"


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "lint_test"
    create_vault(str(p), PASSWORD)
    update_vault(str(p) + ".vault", PASSWORD, "APP_NAME", "envault")
    update_vault(str(p) + ".vault", PASSWORD, "SECRET_KEY", "abc123")
    return str(p) + ".vault"


def test_lint_dict_clean():
    report = lint_dict({"APP_NAME": "envault", "PORT": "8080"})
    assert report.ok


def test_lint_dict_bad_naming():
    report = lint_dict({"appName": "value"})
    assert not report.ok
    assert any(i.rule == "naming" for i in report.issues)


def test_lint_dict_empty_value():
    report = lint_dict({"API_KEY": ""})
    assert not report.ok
    assert any(i.rule == "empty_value" for i in report.issues)


def test_lint_dict_placeholder_value():
    report = lint_dict({"DB_PASSWORD": "changeme"})
    assert not report.ok
    assert any(i.rule == "placeholder" for i in report.issues)


def test_lint_dict_multiple_issues():
    report = lint_dict({"bad-key": "", "GOOD_KEY": "todo"})
    rules = {i.rule for i in report.issues}
    assert "naming" in rules
    assert "empty_value" in rules
    assert "placeholder" in rules


def test_lint_vault_clean(vault_path):
    report = lint_vault(vault_path, PASSWORD)
    assert report.ok


def test_lint_vault_with_issues(vault_path):
    update_vault(vault_path, PASSWORD, "bad_key", "")
    report = lint_vault(vault_path, PASSWORD)
    assert not report.ok


def test_format_report_no_issues():
    report = LintReport()
    assert format_report(report) == "No issues found."


def test_format_report_with_issues():
    report = lint_dict({"bad-key": ""})
    output = format_report(report)
    assert "issue" in output
    assert "naming" in output or "empty_value" in output

"""Tests for envault.validators."""
import pytest
from envault.validators import (
    validate_dict,
    format_report,
    ValidationReport,
)


def test_validate_clean_dict():
    data = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    report = validate_dict(data)
    assert report.ok


def test_validate_empty_value():
    report = validate_dict({"API_KEY": ""})
    assert not report.ok
    assert any("empty" in i.message.lower() for i in report.issues)


def test_validate_lowercase_key():
    report = validate_dict({"api_key": "value"})
    assert not report.ok
    assert any("uppercase" in i.message.lower() for i in report.issues)


def test_validate_whitespace_in_key():
    report = validate_dict({"MY KEY": "value"})
    assert not report.ok
    assert any("whitespace" in i.message.lower() for i in report.issues)


def test_validate_placeholder_value():
    for placeholder in ["changeme", "TODO", "xxx"]:
        report = validate_dict({"SOME_KEY": placeholder})
        assert not report.ok
        assert any("placeholder" in i.message.lower() for i in report.issues)


def test_multiple_issues_same_key():
    report = validate_dict({"bad key": ""})
    keys = [i.key for i in report.issues]
    assert keys.count("bad key") >= 2


def test_format_report_ok():
    report = ValidationReport()
    assert "passed" in format_report(report)


def test_format_report_with_issues():
    report = validate_dict({"api_key": ""})
    text = format_report(report)
    assert "Validation issues" in text
    assert "api_key" in text


def test_extra_rule_applied():
    def must_start_with_app(key, value):
        if not key.startswith("APP_"):
            return "Key must start with APP_."
        return None

    report = validate_dict({"DB_HOST": "localhost"}, extra_rules=[must_start_with_app])
    assert not report.ok
    assert any("APP_" in i.message for i in report.issues)


def test_extra_rule_passes():
    def must_start_with_app(key, value):
        if not key.startswith("APP_"):
            return "Key must start with APP_."
        return None

    report = validate_dict({"APP_HOST": "localhost"}, extra_rules=[must_start_with_app])
    assert report.ok

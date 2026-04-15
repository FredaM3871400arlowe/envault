"""Utilities for parsing and serialising .env file content."""

import re
from typing import Dict

_COMMENT_RE = re.compile(r"^\s*#")
_BLANK_RE = re.compile(r"^\s*$")
_LINE_RE = re.compile(
    r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$"
)


def parse_env(content: str) -> Dict[str, str]:
    """Parse the text content of a .env file into a dictionary.

    Handles:
    - Comments (lines starting with #)
    - Blank lines
    - Optional 'export' prefix
    - Single and double quoted values
    - Inline comments after quoted values are NOT stripped (kept simple)

    Args:
        content: Raw text content of a .env file.

    Returns:
        Dictionary of variable names to their string values.
    """
    result: Dict[str, str] = {}
    for line in content.splitlines():
        if _COMMENT_RE.match(line) or _BLANK_RE.match(line):
            continue
        match = _LINE_RE.match(line)
        if match:
            key, value = match.group(1), match.group(2)
            value = _strip_quotes(value)
            result[key] = value
    return result


def serialise_env(env_vars: Dict[str, str]) -> str:
    """Serialise a dictionary back to .env file format.

    Values containing spaces or special characters are double-quoted.

    Args:
        env_vars: Dictionary of environment variable key-value pairs.

    Returns:
        A string in .env format.
    """
    lines = []
    for key, value in sorted(env_vars.items()):
        if _needs_quoting(value):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (
            value[0] == "'" and value[-1] == "'"
        ):
            return value[1:-1]
    return value


def _needs_quoting(value: str) -> bool:
    """Return True if the value should be wrapped in quotes."""
    return bool(re.search(r"[\s#$\\\"'`]", value))

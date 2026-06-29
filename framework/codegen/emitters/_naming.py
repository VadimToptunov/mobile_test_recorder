"""
Shared identifier-casing helpers for emitters.

Every emitter needs to turn a suite/case name into a language-appropriate
identifier (snake_case file, PascalClass, camelMethod, kebab-file). These were
copy-pasted across ~7 emitter modules; centralise them so the casing rules have
one definition.
"""

from __future__ import annotations


def snake(name: str) -> str:
    """``LoginFlow`` / ``Login flow`` -> ``login_flow``."""
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def kebab(name: str) -> str:
    """``LoginFlow`` -> ``login-flow``."""
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("-")
        out.append(ch.lower())
    return "".join(out).replace(" ", "-").replace("_", "-")


def camel(name: str) -> str:
    """``login_flow`` / ``login-flow`` -> ``loginFlow``."""
    parts = [p for p in name.replace("-", "_").split("_") if p]
    if not parts:
        return "test"
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def pascal(name: str) -> str:
    """``login_flow`` / ``login flow`` -> ``LoginFlow``."""
    parts = [p for p in name.replace("-", "_").replace(" ", "_").split("_") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "Generated"

"""Question-bank entry filters."""

from __future__ import annotations

from typing import Any

FAILED_GENERATION_PREFIX = "[Generation failed]"


def is_failed_generation_question(question: str | None) -> bool:
    return str(question or "").strip().startswith(FAILED_GENERATION_PREFIX)


def is_failed_generation_entry(entry: dict[str, Any]) -> bool:
    return is_failed_generation_question(str(entry.get("question") or ""))


def filter_exportable_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop rows whose question text marks a generation failure."""
    return [entry for entry in entries if not is_failed_generation_entry(entry)]


__all__ = [
    "FAILED_GENERATION_PREFIX",
    "filter_exportable_entries",
    "is_failed_generation_entry",
    "is_failed_generation_question",
]

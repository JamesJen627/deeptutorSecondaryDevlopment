"""Quiz history loaders for question generation dedup.

Used by :class:`QuestionPipeline` so the Explore phase can articulate
which topics have already been tested, which the learner got wrong, and
how the next round should avoid duplication / optionally target weak
spots.

Entry points:

* :func:`load_session_quiz_history` — prior items in one chat session
  (``notebook_entries`` scoped by ``session_id``).
* :func:`load_kb_quiz_history` — prior items across the whole knowledge
  base (``generated_questions`` with answer overlay from ``notebook_entries``).
* :func:`load_quiz_history` — picks KB-wide vs session scope based on
  whether a KB is mounted.

Fails closed: any error returns an empty list.
"""

from __future__ import annotations

import logging
from typing import Any

from deeptutor.agents.question.pipeline import QuizHistoryEntry
from deeptutor.services.question_bank.filters import is_failed_generation_question

logger = logging.getLogger(__name__)

DEFAULT_MAX_ENTRIES = 30
DEFAULT_KB_MAX_ENTRIES = 100


def _history_key(raw: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(raw.get("session_id") or "").strip(),
        str(raw.get("turn_id") or "").strip(),
        str(raw.get("question_id") or "").strip(),
    )


def _notebook_row_to_entry(raw: dict[str, Any]) -> QuizHistoryEntry | None:
    question = str(raw.get("question") or "").strip()
    if not question or is_failed_generation_question(question):
        return None
    user_answer = str(raw.get("user_answer") or "").strip()
    correct_answer = str(raw.get("correct_answer") or "").strip()
    if not user_answer:
        is_correct: bool | None = None
    else:
        is_correct = bool(raw.get("is_correct"))
    return QuizHistoryEntry(
        question=question,
        question_type=str(raw.get("question_type") or "").strip(),
        correct_answer=correct_answer,
        user_answer=user_answer,
        is_correct=is_correct,
        turn_id=str(raw.get("turn_id") or "").strip(),
    )


def _sort_history_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items.sort(key=lambda r: (float(r.get("created_at") or 0.0), int(r.get("id") or 0)))
    return items


def _rows_to_quiz_history_entries(items: list[dict[str, Any]]) -> list[QuizHistoryEntry]:
    entries: list[QuizHistoryEntry] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        entry = _notebook_row_to_entry(raw)
        if entry is not None:
            entries.append(entry)
    return entries


async def load_session_quiz_history(
    session_id: str,
    *,
    max_entries: int = DEFAULT_MAX_ENTRIES,
) -> list[QuizHistoryEntry]:
    """Return prior quiz items for ``session_id`` in chronological order."""
    if not session_id or max_entries <= 0:
        return []
    try:
        from deeptutor.services.session.sqlite_store import get_sqlite_session_store

        store = get_sqlite_session_store()
        result = await store.list_notebook_entries(
            session_id=session_id,
            limit=max(1, int(max_entries)),
            offset=0,
        )
    except Exception:
        logger.warning("Failed to load quiz history for session %s", session_id, exc_info=True)
        return []

    items = _sort_history_rows(list(result.get("items") or []))
    return _rows_to_quiz_history_entries(items)


async def load_kb_quiz_history(
    kb_name: str,
    *,
    max_entries: int = DEFAULT_KB_MAX_ENTRIES,
) -> list[QuizHistoryEntry]:
    """Return prior quiz items for ``kb_name`` across all sessions.

    Primary source: ``generated_questions``. Answer state is overlaid from
    ``notebook_entries`` rows that share the same
    ``(session_id, turn_id, question_id)`` key. When no generated rows
    exist yet (legacy data), falls back to notebook rows tagged with
    ``kb_name``.
    """
    resolved = (kb_name or "").strip()
    if not resolved or max_entries <= 0:
        return []
    try:
        from deeptutor.services.session.sqlite_store import get_sqlite_session_store

        store = get_sqlite_session_store()
        gen_result = await store.list_generated_questions_by_kb(
            resolved,
            limit=max(1, int(max_entries)),
            offset=0,
        )
        gen_items = _sort_history_rows(list(gen_result.get("items") or []))

        nb_result = await store.list_notebook_entries(
            kb_name=resolved,
            limit=max(1, int(max_entries) * 2),
            offset=0,
        )
        answer_overlay = {
            _history_key(raw): raw
            for raw in (nb_result.get("items") or [])
            if isinstance(raw, dict)
        }
    except Exception:
        logger.warning("Failed to load quiz history for KB %s", resolved, exc_info=True)
        return []

    if not gen_items:
        notebook_rows = _sort_history_rows(list(nb_result.get("items") or []))
        return _rows_to_quiz_history_entries(notebook_rows[-max_entries:])

    entries: list[QuizHistoryEntry] = []
    for raw in gen_items:
        overlay = answer_overlay.get(_history_key(raw), {})
        merged = {**raw, **overlay} if overlay else raw
        entry = _notebook_row_to_entry(merged)
        if entry is not None:
            entries.append(entry)
    return entries


async def load_quiz_history(
    *,
    session_id: str = "",
    kb_name: str | None = None,
    max_entries: int | None = None,
) -> list[QuizHistoryEntry]:
    """Load quiz history for question generation.

    When ``kb_name`` is set, returns KB-wide history; otherwise session scope.
    """
    if (kb_name or "").strip():
        limit = max_entries if max_entries is not None else DEFAULT_KB_MAX_ENTRIES
        return await load_kb_quiz_history(kb_name.strip(), max_entries=limit)
    limit = max_entries if max_entries is not None else DEFAULT_MAX_ENTRIES
    return await load_session_quiz_history(session_id, max_entries=limit)


__all__ = [
    "DEFAULT_KB_MAX_ENTRIES",
    "DEFAULT_MAX_ENTRIES",
    "load_kb_quiz_history",
    "load_quiz_history",
    "load_session_quiz_history",
]

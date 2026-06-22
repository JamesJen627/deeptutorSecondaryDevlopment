"""Persist generated quiz items to the question bank and KB history."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deeptutor.agents.question.pipeline import QuizPair
from deeptutor.services.question_bank.filters import is_failed_generation_question

logger = logging.getLogger(__name__)


def _qa_pair_to_notebook_item(
    *,
    qa_pair: QuizPair,
    turn_id: str,
    kb_name: str | None,
) -> dict[str, str | bool | dict[str, str] | None]:
    return {
        "turn_id": turn_id,
        "question_id": qa_pair.question_id,
        "question": qa_pair.question,
        "question_type": qa_pair.question_type,
        "options": qa_pair.options if isinstance(qa_pair.options, dict) else {},
        "correct_answer": qa_pair.correct_answer,
        "explanation": qa_pair.explanation,
        "difficulty": qa_pair.difficulty,
        "kb_name": (kb_name or "").strip(),
        "user_answer": "",
        "is_correct": False,
    }


async def persist_generated_question(
    *,
    session_id: str,
    turn_id: str,
    kb_name: str | None,
    qa_pair: QuizPair,
) -> None:
    """Write one freshly generated question to ``notebook_entries`` and, when
    scoped to a knowledge base, ``generated_questions``.

    Called as each question is emitted so the bank reflects generated items
    before the learner submits an answer.
    """
    if not session_id:
        return
    question = (qa_pair.question or "").strip()
    if not question or is_failed_generation_question(question):
        return

    item = _qa_pair_to_notebook_item(qa_pair=qa_pair, turn_id=turn_id, kb_name=kb_name)
    try:
        from deeptutor.services.session import get_sqlite_session_store

        store = get_sqlite_session_store()
        await store.upsert_notebook_entries(session_id, [item])
    except Exception:
        logger.warning(
            "Failed to persist generated question %s for session %s",
            qa_pair.question_id,
            session_id,
            exc_info=True,
        )
        return

    resolved_kb = (kb_name or "").strip()
    if not resolved_kb:
        return

    generated_item = {
        **item,
        "kb_name": resolved_kb,
        "session_id": session_id,
        "topic": qa_pair.topic or "",
    }
    try:
        await store.upsert_generated_questions([generated_item])
    except Exception:
        logger.warning(
            "Failed to persist generated question %s to KB history %s",
            qa_pair.question_id,
            resolved_kb,
            exc_info=True,
        )


__all__ = ["persist_generated_question"]

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from deeptutor.agents.question.persistence import persist_generated_question
from deeptutor.agents.question.pipeline import QuizPair
from deeptutor.services.session.sqlite_store import SQLiteSessionStore


@pytest.fixture
def tmp_sqlite_store(tmp_path: Path):
    store = SQLiteSessionStore(db_path=tmp_path / "session.db")
    with patch(
        "deeptutor.services.session.get_sqlite_session_store",
        return_value=store,
    ):
        yield store


def test_persist_generated_question_writes_notebook_and_kb_history(
    tmp_sqlite_store: SQLiteSessionStore,
) -> None:
    store = tmp_sqlite_store

    async def run() -> None:
        session = await store.create_session(session_id="s1")
        await persist_generated_question(
            session_id=session["id"],
            turn_id="turn-1",
            kb_name="毛概",
            qa_pair=QuizPair(
                question_id="q_1",
                question="What is socialism?",
                question_type="written",
                correct_answer="A system",
                explanation="Basic definition",
                options=None,
                topic="intro",
                difficulty="easy",
            ),
        )

    asyncio.run(run())

    notebook = asyncio.run(store.list_notebook_entries(session_id="s1"))
    assert notebook["total"] == 1
    entry = notebook["items"][0]
    assert entry["kb_name"] == "毛概"
    assert entry["user_answer"] == ""

    kb_history = asyncio.run(store.list_generated_questions_by_kb("毛概"))
    assert kb_history["total"] == 1
    assert kb_history["items"][0]["topic"] == "intro"


def test_persist_generated_question_skips_failed_generation(
    tmp_sqlite_store: SQLiteSessionStore,
) -> None:
    store = tmp_sqlite_store

    async def run() -> None:
        session = await store.create_session(session_id="s1")
        await persist_generated_question(
            session_id=session["id"],
            turn_id="turn-1",
            kb_name="毛概",
            qa_pair=QuizPair(
                question_id="q_1",
                question="[Generation failed] intro",
                question_type="written",
                correct_answer="N/A",
                explanation="N/A",
            ),
        )

    asyncio.run(run())
    assert asyncio.run(store.list_notebook_entries(session_id="s1"))["total"] == 0
    assert asyncio.run(store.list_generated_questions_by_kb("毛概"))["total"] == 0

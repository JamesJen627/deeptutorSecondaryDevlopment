from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from deeptutor.agents.question.history import (
    load_kb_quiz_history,
    load_quiz_history,
)
from deeptutor.services.session.sqlite_store import SQLiteSessionStore


@pytest.fixture
def tmp_sqlite_store(tmp_path: Path):
    store = SQLiteSessionStore(db_path=tmp_path / "session.db")
    with patch(
        "deeptutor.services.session.sqlite_store.get_sqlite_session_store",
        return_value=store,
    ):
        yield store


def test_load_kb_quiz_history_merges_answer_overlay(tmp_sqlite_store: SQLiteSessionStore) -> None:
    store = tmp_sqlite_store

    async def setup() -> None:
        await store.create_session(session_id="s1")
        await store.create_session(session_id="s2")
        await store.upsert_generated_questions(
            [
                {
                    "kb_name": "毛概",
                    "session_id": "s1",
                    "turn_id": "t1",
                    "question_id": "q_1",
                    "question": "Q from session 1",
                    "question_type": "written",
                    "options": {},
                    "correct_answer": "A",
                    "explanation": "e1",
                    "difficulty": "easy",
                    "topic": "t1",
                },
                {
                    "kb_name": "毛概",
                    "session_id": "s2",
                    "turn_id": "t2",
                    "question_id": "q_1",
                    "question": "Q from session 2",
                    "question_type": "written",
                    "options": {},
                    "correct_answer": "B",
                    "explanation": "e2",
                    "difficulty": "easy",
                    "topic": "t2",
                },
            ]
        )
        await store.upsert_notebook_entries(
            "s1",
            [
                {
                    "turn_id": "t1",
                    "question_id": "q_1",
                    "question": "Q from session 1",
                    "question_type": "written",
                    "options": {},
                    "correct_answer": "A",
                    "explanation": "e1",
                    "difficulty": "easy",
                    "kb_name": "毛概",
                    "user_answer": "wrong",
                    "is_correct": False,
                }
            ],
        )

    asyncio.run(setup())

    entries = asyncio.run(load_kb_quiz_history("毛概"))
    assert len(entries) == 2
    assert entries[0].question == "Q from session 1"
    assert entries[0].is_correct is False
    assert entries[0].user_answer == "wrong"
    assert entries[1].question == "Q from session 2"
    assert entries[1].is_correct is None


def test_load_kb_quiz_history_falls_back_to_notebook(tmp_sqlite_store: SQLiteSessionStore) -> None:
    store = tmp_sqlite_store

    async def setup() -> None:
        await store.create_session(session_id="s1")
        await store.upsert_notebook_entries(
            "s1",
            [
                {
                    "turn_id": "t1",
                    "question_id": "q_1",
                    "question": "Legacy KB question",
                    "question_type": "written",
                    "options": {},
                    "correct_answer": "A",
                    "explanation": "e",
                    "difficulty": "easy",
                    "kb_name": "毛概",
                    "user_answer": "",
                    "is_correct": False,
                }
            ],
        )

    asyncio.run(setup())

    entries = asyncio.run(load_kb_quiz_history("毛概"))
    assert len(entries) == 1
    assert entries[0].question == "Legacy KB question"


def test_load_quiz_history_prefers_kb_scope(tmp_sqlite_store: SQLiteSessionStore) -> None:
    store = tmp_sqlite_store

    async def setup() -> None:
        await store.create_session(session_id="s1")
        await store.create_session(session_id="s2")
        await store.upsert_generated_questions(
            [
                {
                    "kb_name": "毛概",
                    "session_id": "s2",
                    "turn_id": "t9",
                    "question_id": "q_9",
                    "question": "KB-wide question",
                    "question_type": "written",
                    "options": {},
                    "correct_answer": "X",
                    "explanation": "e",
                    "difficulty": "easy",
                    "topic": "t",
                }
            ]
        )
        await store.upsert_notebook_entries(
            "s1",
            [
                {
                    "turn_id": "t1",
                    "question_id": "q_1",
                    "question": "Session-only question",
                    "question_type": "written",
                    "correct_answer": "Y",
                    "explanation": "e",
                    "user_answer": "Y",
                    "is_correct": True,
                }
            ],
        )

    asyncio.run(setup())

    kb_entries = asyncio.run(
        load_quiz_history(session_id="s1", kb_name="毛概")
    )
    assert [e.question for e in kb_entries] == ["KB-wide question"]

    session_entries = asyncio.run(load_quiz_history(session_id="s1"))
    assert [e.question for e in session_entries] == ["Session-only question"]

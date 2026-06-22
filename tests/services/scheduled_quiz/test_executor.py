from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from deeptutor.services.scheduled_quiz.config import ScheduledQuizJob
from deeptutor.services.scheduled_quiz.executor import execute_scheduled_quiz
from deeptutor.services.session.sqlite_store import SQLiteSessionStore


@pytest.fixture
def job() -> ScheduledQuizJob:
    return ScheduledQuizJob(
        id="nightly-maogai",
        kb_name="demo-kb",
        topic="随机考点",
        num_questions=2,
        cron_expr="0 2 * * *",
        auto_export=True,
    )


def test_execute_scheduled_quiz_success(tmp_path: Path, job: ScheduledQuizJob) -> None:
    store = SQLiteSessionStore(db_path=tmp_path / "session.db")
    export_mock = AsyncMock(return_value=tmp_path / "out.xlsx")

    async def run() -> tuple[str, str | None]:
        with (
            patch(
                "deeptutor.services.scheduled_quiz.executor._kb_exists",
                return_value=True,
            ),
            patch(
                "deeptutor.services.session.get_sqlite_session_store",
                return_value=store,
            ),
            patch(
                "deeptutor.services.scheduled_quiz.executor.load_quiz_history",
                new=AsyncMock(return_value=[]),
            ),
            patch(
                "deeptutor.services.scheduled_quiz.executor.load_config_with_main",
                return_value={},
            ),
            patch(
                "deeptutor.services.scheduled_quiz.executor.QuestionPipeline"
            ) as pipeline_cls,
            patch(
                "deeptutor.services.scheduled_quiz.executor._export_turn_entries",
                new=export_mock,
            ),
        ):
            pipeline = pipeline_cls.return_value
            pipeline.run = AsyncMock(
                return_value={"summary": {"completed": 2, "failed": 0, "results": []}}
            )
            return await execute_scheduled_quiz(job)

    status, error = asyncio.run(run())
    assert status == "ok"
    assert error is None
    export_mock.assert_awaited_once()


def test_execute_scheduled_quiz_skips_missing_kb(job: ScheduledQuizJob) -> None:
    with patch("deeptutor.services.scheduled_quiz.executor._kb_exists", return_value=False):
        status, error = asyncio.run(execute_scheduled_quiz(job))
    assert status == "error"
    assert "not found" in (error or "")

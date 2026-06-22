from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

pytest.importorskip("yaml")
pytest.importorskip("croniter")

from deeptutor.services.scheduled_quiz.service import ScheduledQuizService


@pytest.fixture
def service(tmp_path: Path) -> ScheduledQuizService:
    config = tmp_path / "scheduled_quiz.yaml"
    config.write_text(
        """
jobs:
  - id: quick-test
    enabled: true
    kb_name: "demo-kb"
    num_questions: 1
    topic: "test topic"
    cron_expr: "* * * * *"
    timezone: "UTC"
    auto_export: false
""".strip(),
        encoding="utf-8",
    )
    return ScheduledQuizService(
        config_path=config,
        state_path=tmp_path / "state.json",
    )


def test_reload_assigns_next_run(service: ScheduledQuizService) -> None:
    views = service.reload()
    assert len(views) == 1
    assert views[0].state.next_run_at_ms is not None


def test_run_job_records_state(service: ScheduledQuizService) -> None:
    views = service.reload()
    view = views[0]
    view.state.next_run_at_ms = 0

    async def run() -> None:
        with patch(
            "deeptutor.services.scheduled_quiz.service.execute_scheduled_quiz",
            new=AsyncMock(return_value=("ok", None)),
        ):
            await service._run_job(view)

    asyncio.run(run())
    assert view.state.last_status == "ok"
    assert view.state.last_error is None
    assert view.state.next_run_at_ms is not None
    assert len(view.state.run_history) == 1

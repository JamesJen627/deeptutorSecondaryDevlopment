"""Run one scheduled quiz job through QuestionPipeline."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from deeptutor.agents.question.history import load_quiz_history
from deeptutor.agents.question.pipeline import QuestionPipeline
from deeptutor.agents.question.request_config import build_question_runtime_config
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus
from deeptutor.services.config import load_config_with_main
from deeptutor.services.question_bank.export import entries_to_xlsx_bytes
from deeptutor.services.question_bank.filters import filter_exportable_entries
from deeptutor.services.scheduled_quiz.config import ScheduledQuizJob
from deeptutor.services.settings.interface_settings import get_ui_language

logger = logging.getLogger(__name__)


def _resolve_language(job: ScheduledQuizJob) -> str:
    return (job.language or get_ui_language(default="zh") or "en").strip() or "en"


def _kb_exists(kb_name: str) -> bool:
    try:
        from deeptutor.knowledge.manager import KnowledgeManager

        return kb_name in KnowledgeManager().list_knowledge_bases()
    except Exception:
        logger.warning("Failed to verify KB %s", kb_name, exc_info=True)
        return False


async def _ensure_session(session_id: str, *, title: str) -> None:
    from deeptutor.services.session import get_sqlite_session_store

    store = get_sqlite_session_store()
    if await store.get_session(session_id) is None:
        await store.create_session(session_id=session_id, title=title)


async def _drain_stream(stream: StreamBus) -> None:
    async for _event in stream.subscribe():
        pass


async def _export_turn_entries(
    *,
    job: ScheduledQuizJob,
    session_id: str,
    turn_id: str,
) -> Path | None:
    from deeptutor.services.path_service import get_path_service
    from deeptutor.services.session import get_sqlite_session_store

    store = get_sqlite_session_store()
    result = await store.list_notebook_entries(session_id=session_id, limit=500)
    entries = [
        item
        for item in (result.get("items") or [])
        if isinstance(item, dict) and str(item.get("turn_id") or "") == turn_id
    ]
    exportable = filter_exportable_entries(entries)
    if not exportable:
        return None
    exports_dir = get_path_service().user_data_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    path = exports_dir / f"{job.id}-{int(time.time())}.xlsx"
    path.write_bytes(entries_to_xlsx_bytes(exportable))
    logger.info("Scheduled quiz %s exported %d rows to %s", job.id, len(exportable), path)
    return path


async def execute_scheduled_quiz(job: ScheduledQuizJob) -> tuple[str, str | None]:
    """Run ``job`` and return ``(status, error)``."""
    if not job.enabled:
        return "skipped", "job disabled"
    if not _kb_exists(job.kb_name):
        return "error", f"knowledge base not found: {job.kb_name}"

    session_id = f"scheduled-quiz-{job.id}"
    turn_id = f"scheduled-{job.id}-{uuid.uuid4().hex[:8]}"
    language = _resolve_language(job)
    await _ensure_session(
        session_id,
        title=f"Scheduled Quiz · {job.kb_name}",
    )

    quiz_history = await load_quiz_history(session_id=session_id, kb_name=job.kb_name)
    runtime_config = build_question_runtime_config(base_config=load_config_with_main("main.yaml"))
    pipeline = QuestionPipeline(
        language=language,
        kb_name=job.kb_name,
        enabled_tools=["rag"],
        runtime_config=runtime_config,
    )
    context = UnifiedContext(
        session_id=session_id,
        user_message=job.topic,
        enabled_tools=["rag"],
        active_capability="deep_question",
        knowledge_bases=[job.kb_name],
        language=language,
        metadata={
            "turn_id": turn_id,
            "source": "scheduled_quiz",
            "scheduled_quiz_job_id": job.id,
        },
    )

    stream = StreamBus()
    drain_task = asyncio.create_task(_drain_stream(stream))
    try:
        result = await pipeline.run(
            context=context,
            user_message=job.topic,
            num_questions=job.num_questions,
            difficulty=job.difficulty,
            quiz_history=quiz_history,
            stream=stream,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scheduled quiz job %s failed", job.id)
        return "error", f"{type(exc).__name__}: {exc}"
    finally:
        await stream.close()
        try:
            await drain_task
        except Exception:
            logger.debug("Scheduled quiz stream drain failed", exc_info=True)

    summary = result.get("summary") if isinstance(result, dict) else {}
    completed = int((summary or {}).get("completed") or 0) if isinstance(summary, dict) else 0
    if completed <= 0:
        return "error", "no questions generated"

    if job.auto_export:
        try:
            await _export_turn_entries(job=job, session_id=session_id, turn_id=turn_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Scheduled quiz %s export failed: %s", job.id, exc, exc_info=True)

    return "ok", None


__all__ = ["execute_scheduled_quiz"]

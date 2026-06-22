"""Scheduler for YAML-defined scheduled quiz jobs."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from deeptutor.services.cron.service import CronRunRecord, _now_ms, compute_next_run
from deeptutor.services.path_service import get_path_service
from deeptutor.services.scheduled_quiz.config import ScheduledQuizJob, load_scheduled_quiz_jobs
from deeptutor.services.scheduled_quiz.executor import execute_scheduled_quiz

logger = logging.getLogger(__name__)

_MAX_SLEEP_SECONDS = 60.0
_MAX_RUN_HISTORY = 10
_CONFIG_NAME = "scheduled_quiz.yaml"
_STATE_NAME = "scheduled_quiz_state.json"


@dataclass
class ScheduledQuizJobState:
    next_run_at_ms: int | None = None
    last_run_at_ms: int | None = None
    last_status: str | None = None
    last_error: str | None = None
    run_history: list[CronRunRecord] = field(default_factory=list)


@dataclass
class ScheduledQuizJobView:
    job: ScheduledQuizJob
    state: ScheduledQuizJobState


class ScheduledQuizService:
    def __init__(
        self,
        *,
        config_path: Path | None = None,
        state_path: Path | None = None,
    ) -> None:
        paths = get_path_service()
        self.config_path = config_path or paths.get_settings_file(_CONFIG_NAME)
        self.state_path = state_path or paths.get_settings_file(_STATE_NAME)
        self._states: dict[str, ScheduledQuizJobState] = {}
        self._loaded_state = False
        self._timer_task: asyncio.Task | None = None
        self._wake = asyncio.Event()
        self._running = False

    def _load_state(self) -> None:
        if self._loaded_state:
            return
        self._loaded_state = True
        if not self.state_path.exists():
            return
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            raw_jobs = data.get("jobs") if isinstance(data, dict) else {}
            if not isinstance(raw_jobs, dict):
                return
            for job_id, raw_state in raw_jobs.items():
                if not isinstance(raw_state, dict):
                    continue
                history = [
                    CronRunRecord(**record)
                    for record in raw_state.get("run_history", [])
                    if isinstance(record, dict)
                ]
                self._states[str(job_id)] = ScheduledQuizJobState(
                    next_run_at_ms=raw_state.get("next_run_at_ms"),
                    last_run_at_ms=raw_state.get("last_run_at_ms"),
                    last_status=raw_state.get("last_status"),
                    last_error=raw_state.get("last_error"),
                    run_history=history,
                )
        except Exception:
            logger.exception("Failed to load scheduled quiz state from %s", self.state_path)

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "jobs": {
                job_id: {
                    **asdict(state),
                    "run_history": [asdict(record) for record in state.run_history],
                }
                for job_id, state in self._states.items()
            },
        }
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    def reload(self) -> list[ScheduledQuizJobView]:
        self._load_state()
        now = _now_ms()
        views: list[ScheduledQuizJobView] = []
        active_ids: set[str] = set()
        for job in load_scheduled_quiz_jobs(self.config_path):
            active_ids.add(job.id)
            state = self._states.setdefault(job.id, ScheduledQuizJobState())
            if state.next_run_at_ms is None:
                state.next_run_at_ms = compute_next_run(job.to_schedule(), now)
            views.append(ScheduledQuizJobView(job=job, state=state))
        for stale_id in [job_id for job_id in self._states if job_id not in active_ids]:
            del self._states[stale_id]
        self._save_state()
        self._wake.set()
        return views

    def list_jobs(self) -> list[ScheduledQuizJobView]:
        return self.reload()

    async def start(self) -> None:
        if self._running:
            return
        self.reload()
        self._running = True
        self._timer_task = asyncio.create_task(self._loop(), name="scheduled-quiz:scheduler")
        logger.info(
            "Scheduled quiz service started (%d jobs, config=%s)",
            len(self.list_jobs()),
            self.config_path,
        )

    async def stop(self) -> None:
        self._running = False
        if self._timer_task:
            self._timer_task.cancel()
            try:
                await self._timer_task
            except asyncio.CancelledError:
                pass
            self._timer_task = None

    async def _loop(self) -> None:
        while self._running:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Scheduled quiz tick failed")
            sleep_s = self._seconds_until_next_due()
            self._wake.clear()
            try:
                await asyncio.wait_for(self._wake.wait(), timeout=sleep_s)
            except asyncio.TimeoutError:
                pass

    def _seconds_until_next_due(self) -> float:
        views = self.list_jobs()
        due_times = [
            view.state.next_run_at_ms
            for view in views
            if view.job.enabled and view.state.next_run_at_ms
        ]
        if not due_times:
            return _MAX_SLEEP_SECONDS
        delta_s = (min(due_times) - _now_ms()) / 1000
        return max(0.05, min(delta_s, _MAX_SLEEP_SECONDS))

    async def _tick(self) -> None:
        now = _now_ms()
        for view in self.list_jobs():
            if not view.job.enabled or not view.state.next_run_at_ms:
                continue
            if view.state.next_run_at_ms > now:
                continue
            await self._run_job(view)

    async def _run_job(self, view: ScheduledQuizJobView) -> None:
        job = view.job
        state = view.state
        started = _now_ms()
        status, error = await execute_scheduled_quiz(job)
        state.last_run_at_ms = started
        state.last_status = status
        state.last_error = error
        state.run_history.append(
            CronRunRecord(
                run_at_ms=started,
                status=status,
                duration_ms=_now_ms() - started,
                error=error,
            )
        )
        state.run_history = state.run_history[-_MAX_RUN_HISTORY:]
        state.next_run_at_ms = compute_next_run(job.to_schedule(), _now_ms())
        self._save_state()
        if status == "ok":
            logger.info("Scheduled quiz job %s completed", job.id)
        else:
            logger.warning("Scheduled quiz job %s finished with %s: %s", job.id, status, error)


_service: ScheduledQuizService | None = None


def get_scheduled_quiz_service() -> ScheduledQuizService:
    global _service
    if _service is None:
        _service = ScheduledQuizService()
    return _service


__all__ = [
    "ScheduledQuizJobState",
    "ScheduledQuizJobView",
    "ScheduledQuizService",
    "get_scheduled_quiz_service",
]

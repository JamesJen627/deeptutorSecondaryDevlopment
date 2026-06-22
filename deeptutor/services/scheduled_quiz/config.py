"""Scheduled quiz job configuration (YAML)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from deeptutor.services.cron.service import CronSchedule, compute_next_run, validate_schedule


@dataclass
class ScheduledQuizJob:
    id: str
    kb_name: str
    topic: str
    num_questions: int
    cron_expr: str
    enabled: bool = True
    timezone: str = "Asia/Shanghai"
    auto_export: bool = False
    difficulty: str = ""
    language: str = ""

    def to_schedule(self) -> CronSchedule:
        return CronSchedule(kind="cron", expr=self.cron_expr, tz=self.timezone or None)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ScheduledQuizJob":
        job_id = str(raw.get("id") or "").strip()
        if not job_id:
            raise ValueError("scheduled quiz job requires id")
        kb_name = str(raw.get("kb_name") or "").strip()
        if not kb_name:
            raise ValueError(f"job {job_id!r} requires kb_name")
        topic = str(raw.get("topic") or "").strip()
        if not topic:
            raise ValueError(f"job {job_id!r} requires topic")
        cron_expr = str(raw.get("cron_expr") or "").strip()
        if not cron_expr:
            raise ValueError(f"job {job_id!r} requires cron_expr")
        num_questions = int(raw.get("num_questions") or 0)
        if num_questions < 1:
            raise ValueError(f"job {job_id!r} num_questions must be >= 1")
        validate_schedule(CronSchedule(kind="cron", expr=cron_expr, tz=raw.get("timezone") or None))
        return cls(
            id=job_id,
            kb_name=kb_name,
            topic=topic,
            num_questions=num_questions,
            cron_expr=cron_expr,
            enabled=bool(raw.get("enabled", True)),
            timezone=str(raw.get("timezone") or "Asia/Shanghai").strip() or "Asia/Shanghai",
            auto_export=bool(raw.get("auto_export", False)),
            difficulty=str(raw.get("difficulty") or "").strip(),
            language=str(raw.get("language") or "").strip(),
        )


def load_scheduled_quiz_jobs(path: Path) -> list[ScheduledQuizJob]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    raw_jobs = data.get("jobs")
    if not isinstance(raw_jobs, list):
        return []
    jobs: list[ScheduledQuizJob] = []
    for raw in raw_jobs:
        if not isinstance(raw, dict):
            continue
        jobs.append(ScheduledQuizJob.from_dict(raw))
    return jobs


__all__ = ["ScheduledQuizJob", "load_scheduled_quiz_jobs"]

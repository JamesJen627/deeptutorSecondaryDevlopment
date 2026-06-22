"""Scheduled quiz API — list jobs and reload YAML config."""

from __future__ import annotations

from fastapi import APIRouter

from deeptutor.services.scheduled_quiz.service import ScheduledQuizJobView, get_scheduled_quiz_service

router = APIRouter()


def _job_payload(view: ScheduledQuizJobView) -> dict:
    job = view.job
    state = view.state
    return {
        "id": job.id,
        "enabled": job.enabled,
        "kb_name": job.kb_name,
        "topic": job.topic,
        "num_questions": job.num_questions,
        "cron_expr": job.cron_expr,
        "timezone": job.timezone,
        "auto_export": job.auto_export,
        "difficulty": job.difficulty,
        "language": job.language,
        "next_run_at_ms": state.next_run_at_ms,
        "last_run_at_ms": state.last_run_at_ms,
        "last_status": state.last_status,
        "last_error": state.last_error,
        "run_history": [
            {
                "run_at_ms": record.run_at_ms,
                "status": record.status,
                "duration_ms": record.duration_ms,
                "error": record.error,
            }
            for record in state.run_history
        ],
    }


@router.get("/jobs")
async def list_jobs():
    service = get_scheduled_quiz_service()
    views = service.list_jobs()
    return {
        "config_path": str(service.config_path),
        "jobs": [_job_payload(view) for view in views],
    }


@router.post("/reload")
async def reload_jobs():
    service = get_scheduled_quiz_service()
    views = service.reload()
    return {"reloaded": True, "count": len(views)}

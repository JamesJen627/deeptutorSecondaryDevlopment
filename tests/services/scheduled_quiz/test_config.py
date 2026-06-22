from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("yaml")
pytest.importorskip("croniter")

from deeptutor.services.scheduled_quiz.config import ScheduledQuizJob, load_scheduled_quiz_jobs


def test_load_scheduled_quiz_jobs(tmp_path: Path) -> None:
    config = tmp_path / "scheduled_quiz.yaml"
    config.write_text(
        """
jobs:
  - id: nightly-maogai
    enabled: true
    kb_name: "毛概"
    num_questions: 3
    topic: "随机热点考点"
    cron_expr: "0 2 * * *"
    timezone: "Asia/Shanghai"
    auto_export: true
""".strip(),
        encoding="utf-8",
    )
    jobs = load_scheduled_quiz_jobs(config)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.id == "nightly-maogai"
    assert job.kb_name == "毛概"
    assert job.num_questions == 3
    assert job.auto_export is True
    assert job.to_schedule().kind == "cron"


def test_scheduled_quiz_job_requires_fields() -> None:
    with pytest.raises(ValueError, match="requires id"):
        ScheduledQuizJob.from_dict({"kb_name": "x", "topic": "t", "cron_expr": "0 2 * * *"})

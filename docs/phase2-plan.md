# Phase 2 — 好用

## 目标

在 Phase 1 稳定可用的基础上，提升速度、去重质量与运维体验。

## 里程碑

| ID | 任务 | 说明 |
|----|------|------|
| P2-M1 | 并行 Worker 池 | Plan 后 `Semaphore(6)` 并发 `_quiz_one` |
| P2-M2 | Dedup Gate | KB 历史 + 本次 topic/stem 中央查重 |
| P2-M3 | Embedding 去重 | 相似度 > 0.85 自动重出（最多 2 次） |
| P2-M4 | Topic 矩阵 Planner | N 章节 × M 考点，强制覆盖 |
| P2-M5 | UI：100 题 + 分批进度 | 4×25 批，可中断续跑 |
| P2-M6 | 定时任务 Web 管理页 | 列表 / 启用 / 日志 / 下次运行时间 |
| P2-M7 | 题库管理 | 按 KB 浏览、筛选、分 sheet 导出 |
| P2-M8 | 失败题自动 repair | 降低 `[Generation failed]` |
| P2-M9 | （可选）向上游提 PR | Apache-2.0 允许 |

## 定时出题增强（Phase 2）

- 任务队列：多 KB、多时间段
- 失败重试 + 邮件/桌面通知
- 与 Windows 服务 / Docker 部署文档
- 并发夜间批次（在 Dedup Gate 就绪后）

## 架构（完成后）

```
Web UI ──► API ──► QuestionPipeline
              ├── KB History Service ──► generated_questions
              ├── ScheduledQuizExecutor ──► CronService
              ├── Dedup Gate (P2)
              └── Export XLSX
```

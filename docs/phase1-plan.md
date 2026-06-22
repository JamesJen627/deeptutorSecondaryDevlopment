# Phase 1 — 能用（Secondary Development）

> Fork: [JamesJen627/deeptutorSecondaryDevlopment](https://github.com/JamesJen627/deeptutorSecondaryDevlopment)  
> Upstream: [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor)

## 目标

1. KB 级历史去重（整个知识库范围）
2. 生成成功即入库（不要求用户作答）
3. 手动「导出 Excel」按钮
4. **定时自动出题**（睡觉时后台跑）
5. 100 题 UI 上限 **暂缓**（定时任务配置里指定题量即可）

## 里程碑

| ID | 任务 | 验收 |
|----|------|------|
| M1 | Fork 本地 dev 跑通 | `pip install -e .` + 前后端可启动 |
| M2 | `notebook_entries` 增加 `kb_name` | 新题带 KB 标签 |
| M3 | `generated_questions` 表 + 生成后写入 | 未作答的题也持久化 |
| M4 | `load_kb_quiz_history(kb_name)` | Planner/Explore 注入 KB 全历史 |
| M5 | Export API + 前端导出按钮 | 表头：题目/选项A-D/答案/解析 |
| M6 | **定时出题 Scheduled Quiz** | 见下文 |
| M7 | 文档 + Windows 常驻运行说明 | [docs/m7-windows-scheduled-quiz.md](m7-windows-scheduled-quiz.md)（含备考两晚示例） |

## M6 — 定时自动出题（第一期方案）

DeepTutor 上游已有内置 **Cron 服务**（`deeptutor/services/cron/`），目前主要用于 Chat 提醒。  
第二期 fork 扩展为 **`quiz` 类型定时任务**：

```
用户配置（Web 或 YAML）
  kb_name, num_questions, topic/difficulty, cron_expr (如 0 2 * * *)
        ↓
CronService 到点触发
        ↓
ScheduledQuizExecutor → QuestionPipeline.run()
        ↓
写入 generated_questions + events
        ↓
（可选）自动导出 xlsx 到 data/user/exports/
```

### 前提条件（用户侧）

- 电脑睡眠前 **`deeptutor start` 保持运行**（或注册为 Windows 计划任务启动服务）
- 系统 **勿深度睡眠**（仅关屏可；S3/S4 会暂停进程）
- 已配置 LLM API Key

### 配置示例（计划中的 YAML）

路径：`data/user/settings/scheduled_quiz.yaml`

```yaml
jobs:
  - id: nightly-maogai
    enabled: true
    kb_name: "毛概"
    num_questions: 40
    topic: "随机热点考点，难度 mixed"
    cron_expr: "0 2 * * *"   # 每天 02:00
    timezone: "Asia/Shanghai"
    auto_export: true
```

## 分支

- 开发分支：`dev/phase1`
- 合并目标：`main`（本 fork 的主线）

## 不在第一期

- 多 Agent 并行出题
- Embedding 相似度去重
- UI 滑块 100 题（用定时任务题量代替）

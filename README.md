# DeepTutor Secondary Development

基于 [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) 的**二次开发 Fork**，面向「按知识库出题 → 去重 → 入库 → 导出 Excel → 定时夜间出题」场景。

> 这不是官方 DeepTutor 仓库。官方文档、Release 与社区请见 **[HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor)**；本仓库保留的完整上游 README 见 **[README_UPSTREAM.md](README_UPSTREAM.md)**。

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)
[![Upstream](https://img.shields.io/badge/Upstream-HKUDS%2FDeepTutor-181717?style=flat-square&logo=github)](https://github.com/HKUDS/DeepTutor)

---

## 本 Fork 多了什么（Phase 1）

| 功能 | 说明 |
|------|------|
| **KB 级去重** | 同一知识库下的历史题目注入 Explore/Plan，减少重复出题 |
| **生成即入库** | 题目生成后写入 Question Bank，无需用户先作答 |
| **`kb_name` 标签** | 每道题记录来源知识库，支持按 KB 筛选与分别导出 |
| **导出 Excel** | Question Bank 一键导出（题目 / 选项 A–D / 答案 / 解析） |
| **定时出题** | `scheduled_quiz.yaml` 配置 cron，夜间自动跑 `deep_question` |
| **历史回填** | 启动时尝试为旧题补全 `kb_name`（来自 session 或生成记录） |

详细计划：[docs/phase1-plan.md](docs/phase1-plan.md) · 路线图 Phase 2：[docs/phase2-plan.md](docs/phase2-plan.md)

---

## 两个目录，别搞混

| 用途 | 路径（本机示例） |
|------|------------------|
| **源码 / Git 仓库** | `D:\Dev\deeptutorSecondaryDevlopment` → 推送到本 GitHub 仓库 |
| **运行工作区（数据）** | `D:\Dev\DeepTutor` → 知识库 PDF、聊天记录、题库 DB、YAML 配置 |

GitHub 上只有**程序源码**；你的毛概/习概知识库和 88 道题在 **`--home` 工作区**，默认不会上传。

---

## 快速开始（Windows）

> 若 `pip` / `deeptutor` 不在 PATH，请用完整路径或 `scripts\` 下脚本。  
> **CMD** 请用 `scripts\dev-start.bat`，不要直接双击 `.ps1`。

```cmd
cd /d D:\Dev\deeptutorSecondaryDevlopment
scripts\dev-install.bat    REM 首次
scripts\dev-start.bat      REM 启动（工作区 D:\Dev\DeepTutor）
```

手动安装与启动见 [SECONDARY_DEV.md](SECONDARY_DEV.md)。

---

## 定时出题（示例）

在工作区创建 `data/user/settings/scheduled_quiz.yaml`：

```yaml
jobs:
  - id: nightly-maogai
    enabled: true
    kb_name: "毛概"
    num_questions: 40
    topic: "随机热点考点"
    cron_expr: "0 2 * * *"
    timezone: "Asia/Shanghai"
    auto_export: true
```

服务需保持运行；深度睡眠会暂停定时任务。Windows 常驻说明见 Phase 1 的 **M7**（待补文档）。

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [SECONDARY_DEV.md](SECONDARY_DEV.md) | 开发路径、启动方式、分支策略 |
| [UPSTREAM.md](UPSTREAM.md) | 如何同步官方新版本 |
| [README_UPSTREAM.md](README_UPSTREAM.md) | 官方 DeepTutor 完整 README（镜像） |
| [AGENTS.md](AGENTS.md) | 架构与 Capability / Tool 说明 |

---

## 与上游的关系

```
HKUDS/DeepTutor  ──fork──▶  JamesJen627/deeptutorSecondaryDevlopment
       │                              │
       │                              ├── 本 README（Fork 说明）
       │                              ├── Phase 1 补丁（出题/导出/定时）
       └── 官方 Release / 文档         └── pip install -e . + deeptutor start --home ...
```

同步上游：`git fetch upstream && git merge upstream/main`（详见 [UPSTREAM.md](UPSTREAM.md)）。

---

## License

与上游相同：[Apache-2.0](LICENSE)。

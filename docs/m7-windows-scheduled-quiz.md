# M7 — Windows 常驻运行与定时出题

> Phase 1 文档 · 配合 [phase1-plan.md](phase1-plan.md) 中的 **M6 定时出题** 使用  
> 适用环境：Windows 10/11，本 Fork 开发机（D 盘路径示例）

定时出题在 **DeepTutor 后端进程运行期间** 由内置调度器触发。  
电脑进入 **休眠 / 睡眠（S3/S4）** 后进程会暂停，到点 **不会** 自动执行——因此需要本指南中的「常驻运行 + 电源策略 +（可选）开机自启」。

---

## 1. 两个目录（再次确认）

| 用途 | 路径 |
|------|------|
| **源码**（改代码、Git） | `D:\Dev\deeptutorSecondaryDevlopment` |
| **运行工作区**（数据、`--home`） | `D:\Dev\DeepTutor` |

以下所有 **配置、日志、导出、知识库** 路径均相对于 **`D:\Dev\DeepTutor`**，除非你显式指定别的 `--home`。

---

## 2. 前提条件

在配置定时任务前，请确认：

- [ ] 已在 **Settings** 中配置可用的 **LLM API Key**
- [ ] 知识库已创建并完成索引（例如「毛概」「习近平新时代中国特色社会主义思想概论」）
- [ ] 知识库名称与 YAML 里 `kb_name` **完全一致**（区分大小写与全角符号）
- [ ] 已安装本 Fork 源码：`pip install -e D:\Dev\deeptutorSecondaryDevlopment`（含 server 依赖）
- [ ] 已安装 **croniter**（定时解析依赖）：
  ```cmd
  D:\python3.12\python.exe -m pip install "croniter>=6.0.0,<7.0.0"
  ```
  若缺失，后端启动日志会出现 `Failed to start scheduled quiz service`，定时任务不会运行。

---

## 3. 启动并保持服务运行

### 3.1 日常开发启动（推荐）

**CMD：**

```cmd
cd /d D:\Dev\deeptutorSecondaryDevlopment
scripts\dev-start.bat
```

脚本等价于：

```powershell
cd D:\Dev\DeepTutor
D:\python3.12\Scripts\deeptutor.exe start --home D:\Dev\DeepTutor
```

默认端口（以终端输出为准，常见为 **8001** 后端、**3782** 前端）。  
**请保持该窗口打开**；关闭窗口即停止服务，夜间任务不会执行。

浏览器访问：`http://127.0.0.1:3782`（或启动日志里打印的前端地址）。

### 3.2 仅启动后端（无前端 UI）

若只需要定时出题、不需要浏览器：

```cmd
cd /d D:\Dev\DeepTutor
D:\python3.12\Scripts\deeptutor.exe serve --home D:\Dev\DeepTutor --port 8001
```

定时调度器随 API 进程 **lifespan** 启动，不依赖前端。

### 3.3 电源与睡眠（重要）

| 场景 | 定时出题能否执行 |
|------|------------------|
| 仅 **关闭显示器** / 锁屏 | ✅ 可以（进程仍在跑） |
| **睡眠 / 休眠**（合盖休眠等） | ❌ 不可以 |
| **关机 / 注销** | ❌ 不可以 |
| **重启后未再启动 deeptutor** | ❌ 不可以 |

**建议设置（控制面板 → 电源选项）：**

- 「使计算机进入睡眠状态」→ **从不**（至少接电源时设为从不）
- 笔记本合盖动作 → 改为 **不采取任何操作** 或 **仅关闭显示器**（按你的习惯）

> 仅关屏不等于休眠；若任务仍未触发，先检查 deeptutor 窗口是否还在、8001 是否可访问。

---

## 4. 配置文件 `scheduled_quiz.yaml`

**路径：**

```text
D:\Dev\DeepTutor\data\user\settings\scheduled_quiz.yaml
```

若文件不存在，可新建。修改后需 **重载配置**（见第 6 节）或 **重启 deeptutor**。

### 4.1 完整示例（毛概 + 习概，各一份 Excel）

```yaml
jobs:
  - id: nightly-maogai
    enabled: true
    kb_name: "毛概"
    num_questions: 40
    topic: "随机热点考点，单选为主，难度 mixed"
    cron_expr: "0 2 * * *"      # 每天 02:00
    timezone: "Asia/Shanghai"
    auto_export: true
    difficulty: ""               # 可选：easy / medium / hard / mixed
    language: "zh"               # 可选，默认跟 UI 语言

  - id: nightly-xigai
    enabled: true
    kb_name: "习近平新时代中国特色社会主义思想概论"
    num_questions: 40
    topic: "随机热点考点，单选为主，难度 mixed"
    cron_expr: "0 3 * * *"      # 每天 03:00（错开 LLM 峰值）
    timezone: "Asia/Shanghai"
    auto_export: true
    language: "zh"
```

### 4.2 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 任务唯一 ID，也用于导出文件名前缀 |
| `enabled` | | `true` / `false`，临时关闭某 job 可设 `false` |
| `kb_name` | ✅ | 与 Knowledge 里知识库 **名称完全一致** |
| `num_questions` | ✅ | 本次生成题数（≥1） |
| `topic` | ✅ | 传给出题 pipeline 的主题描述 |
| `cron_expr` | ✅ | 5 段 cron，如 `0 2 * * *` = 每天 02:00 |
| `timezone` | | 默认 `Asia/Shanghai` |
| `auto_export` | | `true` 时本次运行生成的题导出为 xlsx |
| `difficulty` | | 可选难度 hint |
| `language` | | 出题语言，如 `zh` / `en` |

### 4.3 Cron 表达式速查

```text
分 时 日 月 周
0  2  *  *  *     每天 02:00
0  */6 *  *  *     每 6 小时整点
30 1  *  *  1-5   工作日 01:30
0  1  *  *  *     每天 01:00（凌晨 1 点整）
```

### 4.4 备考两晚示例（每 KB 共 100 题 · 凌晨 1 点起）

**场景：** 只剩两晚备考，目标为 **毛概 100 题 + 习概 100 题**；采用 **每晚每 KB 各 50 题**，共两晚跑完；最终从 **Question Bank 按 KB 分别导出 Excel** 刷题。

**时间线：**

| 晚次 | 01:00 | 03:30（错开，避免两个 job 同时占满 LLM） |
|------|-------|-------------------------------------------|
| 第一晚 | 毛概 +50 | 习概 +50 |
| 第二晚 | 毛概 +50 | 习概 +50 |
| **合计** | 毛概 100 | 习概 100 |

> 50 题一批通常需 **1～3 小时**（视模型与 KB 大小而定）。习概排在 03:30，尽量等毛概跑完再开；若毛概仍在跑，可把习概改为 `0 4 * * *` 或 `0 5 * * *`。

#### 步骤 1 — 第一晚开始前

1. 确认 **deeptutor 已启动** 且 **电脑不会休眠**（见 §3.3）。
2. 创建或覆盖 `D:\Dev\DeepTutor\data\user\settings\scheduled_quiz.yaml`：

```yaml
jobs:
  - id: exam-maogai-nightly
    enabled: true
    kb_name: "毛概"
    num_questions: 50
    topic: "全书随机热点，单选为主，难度 mixed，与已有题库尽量不重复"
    cron_expr: "0 1 * * *"       # 每天 01:00
    timezone: "Asia/Shanghai"
    auto_export: true            # 当晚批次 → exports/（可选备份）
    language: "zh"

  - id: exam-xigai-nightly
    enabled: true
    kb_name: "习近平新时代中国特色社会主义思想概论"
    num_questions: 50
    topic: "全书随机热点，单选为主，难度 mixed，与已有题库尽量不重复"
    cron_expr: "30 3 * * *"      # 每天 03:30（错开毛概）
    timezone: "Asia/Shanghai"
    auto_export: true
    language: "zh"
```

3. 重载配置（或重启 deeptutor）：

```cmd
curl -X POST http://127.0.0.1:8001/api/v1/scheduled-quiz/reload
curl http://127.0.0.1:8001/api/v1/scheduled-quiz/jobs
```

确认两个 job 的 `next_run_at_ms` 指向 **今晚** 的 01:00 / 03:30。

#### 步骤 2 — 第一晚结束后（次日白天）

1. 打开 `scheduled_quiz_state.json`，确认 `last_status` 均为 `ok`。
2. Web → **Question Bank** → 知识库下拉选 **毛概**，看总数是否 +50；再选 **习概** 核对。
3. （可选）查看 `D:\Dev\DeepTutor\data\user\exports\` 当晚自动导出的 xlsx（**仅含该晚 50 题**，不是全库）。

**第二晚会自动再跑一轮**（cron 为每天），无需改 YAML — 只要 **不要关 deeptutor、不要休眠**。

#### 步骤 3 — 第二晚结束后（备考导出）

两晚跑完后，每个 KB 应累计 **约 100 道新题**（含 KB 级去重；若某晚失败，见 §9 排查后手动补跑）。

**按 KB 导出全部题目（推荐，用于刷题）：**

1. 浏览器打开 Question Bank（Space 或 `/notebook`）。
2. 知识库下拉选 **「毛概」** → 点击 **Export Excel** → 得到毛概全集 xlsx。
3. 再选 **「习近平新时代中国特色社会主义思想概论」** → **Export Excel** → 得到习概全集 xlsx。

表头：题目 / 选项 A–D / 答案 / 解析。

**API 等价导出（可选）：**

```text
http://127.0.0.1:8001/api/v1/question-notebook/entries/export?kb_name=毛概
http://127.0.0.1:8001/api/v1/question-notebook/entries/export?kb_name=习近平新时代中国特色社会主义思想概论
```

#### 步骤 4 — 两晚结束后关闭定时

备考结束后，避免第三晚继续出题，任选其一：

**A. 全部禁用**

```yaml
jobs:
  - id: exam-maogai-nightly
    enabled: false
    # ... 其余字段保留 ...
  - id: exam-xigai-nightly
    enabled: false
    # ...
```

**B. 删除 YAML 中 jobs 或清空 `jobs: []`**

然后 `POST /api/v1/scheduled-quiz/reload`。

#### 补跑：若某晚失败或想提前开跑

不必等到凌晨，可在 CMD **手动**补 50 题（同样入库、带去重）：

```cmd
cd /d D:\Dev\DeepTutor

D:\python3.12\Scripts\deeptutor.exe run deep_question "全书随机热点，单选，mixed，与已有题库尽量不重复" --kb 毛概 --config num_questions=50 -l zh

D:\python3.12\Scripts\deeptutor.exe run deep_question "全书随机热点，单选，mixed，与已有题库尽量不重复" --kb 习近平新时代中国特色社会主义思想概论 --config num_questions=50 -l zh
```

#### 备考两晚检查清单

```text
□ 第一晚 20:00 前：deeptutor 已启动，睡眠已关
□ YAML 已写入，reload 后 next_run_at 正确
□ 第一晚上午：state.json 两个 job 均为 ok，Question Bank 各 +50
□ 第二晚上午：同上，各 KB 累计约 100
□ 导出：Question Bank 按 KB 各 Export Excel 一份
□ 关闭：enabled: false 或删除 jobs
```

---

## 5. 定时任务运行时会做什么

```text
到点 → ScheduledQuizExecutor
     → deep_question（QuestionPipeline + RAG）
     → 写入 Question Bank（notebook_entries，带 kb_name）
     → 写入 generated_questions（KB 级历史，供去重）
     → （可选）auto_export → data/user/exports/{job_id}-{timestamp}.xlsx
```

- 每次运行使用独立 session：`scheduled-quiz-{job.id}`
- **auto_export 只导出该次运行生成的题目**，不是该 KB 的全部历史
- 若要导出库里 **所有** 毛概/习概题：在 Web **Question Bank** 按知识库筛选后点 **Export Excel**

**导出目录：**

```text
D:\Dev\DeepTutor\data\user\exports\
```

**运行状态文件：**

```text
D:\Dev\DeepTutor\data\user\settings\scheduled_quiz_state.json
```

含 `last_run_at_ms`、`last_status`、`last_error`、最近 10 次 `run_history`。

---

## 6. 修改配置后如何生效

### 方式 A — HTTP API（无需重启）

```text
GET  http://127.0.0.1:8001/api/v1/scheduled-quiz/jobs
POST http://127.0.0.1:8001/api/v1/scheduled-quiz/reload
```

浏览器或 curl 均可。`jobs` 响应里包含 `config_path`、`next_run_at_ms`、`last_status` 等。

### 方式 B — 重启 deeptutor

停止当前窗口（Ctrl+C）后重新运行 `scripts\dev-start.bat`。

---

## 7. 如何确认配置成功

### 7.1 看 API

```cmd
curl http://127.0.0.1:8001/api/v1/scheduled-quiz/jobs
```

期望：列出你在 YAML 里配置的 `jobs`，且 `enabled: true` 的条目有 `next_run_at_ms`。

### 7.2 看状态文件

打开 `scheduled_quiz_state.json`，检查某 job 的：

- `last_status`: `ok` / `error` / `skipped`
- `last_error`: 失败原因（如 `knowledge base not found: xxx`）

### 7.3 看日志

```text
D:\Dev\DeepTutor\data\user\logs\deeptutor.jsonl
```

搜索 `Scheduled quiz` 或 job `id`。

### 7.4 看 Question Bank

Web → **Question Bank**，按知识库筛选；定时任务成功后应有新题（带对应 `kb_name`）。

---

## 8. 开机自动启动（Windows 任务计划程序）

适合「人不在电脑前，但希望登录后自动跑 deeptutor」的场景。  
**注意：** 若电脑处于休眠，任务计划程序也无法唤醒 LLM 出题（除非额外配置唤醒策略，一般不建议依赖）。

### 8.1 准备启动脚本

在 `D:\Dev\deeptutorSecondaryDevlopment\scripts\` 下已有 `dev-start.bat`。  
若希望 **最小化到后台、不弹 CMD 窗口**，可另建 `start-scheduled-quiz-hidden.vbs`：

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c D:\Dev\deeptutorSecondaryDevlopment\scripts\dev-start.bat", 0, False
```

（`0` = 隐藏窗口；调试阶段建议仍用可见窗口，方便看报错。）

### 8.2 创建计划任务（图形界面）

1. `Win + R` → 输入 `taskschd.msc` → 回车  
2. **创建任务**（不要选「创建基本任务」，以便更多选项）  
3. **常规**  
   - 名称：`DeepTutor Scheduled Quiz`  
   - 勾选「不管用户是否登录都要运行」按需（通常 **仅登录时** 即可）  
   - 勾选「使用最高权限运行」按需（一般不需要）  
4. **触发器** → 新建 → **登录时**（或「启动时」，按你需要）  
5. **操作** → 新建 →  
   - 操作：启动程序  
   - 程序：`D:\Dev\deeptutorSecondaryDevlopment\scripts\dev-start.bat`  
   - 起始于：`D:\Dev\deeptutorSecondaryDevlopment`  
6. **条件** → 取消「只有在计算机使用交流电源时才启动」（笔记本建议取消，否则电池模式不跑）  
7. **设置** → 勾选「如果任务失败，按以下方式重新启动」（可选，间隔 5 分钟）

保存后：**右键任务 → 运行**，确认 8001/3782 正常后再依赖夜间 cron。

### 8.3 命令行创建（可选）

在 **管理员 CMD** 中（路径按你机器修改）：

```cmd
schtasks /Create /TN "DeepTutor Scheduled Quiz" /TR "D:\Dev\deeptutorSecondaryDevlopment\scripts\dev-start.bat" /SC ONLOGON /RL LIMITED /F
```

---

## 9. 常见问题

### Q1：`last_status: error`，`knowledge base not found`

- Knowledge 里不存在该名称的 KB，或名称与 YAML 不一致  
- 在 Web **Knowledge** 页复制 **精确名称** 填入 `kb_name`

### Q2：到点没有任何反应

1. deeptutor 进程是否仍在运行？  
2. 电脑是否睡了？  
3. `croniter` 是否已安装？看启动日志是否有 scheduled quiz 警告  
4. `enabled: false` 或 YAML 语法错误？  
5. 调用 `POST /api/v1/scheduled-quiz/reload` 后看 `next_run_at_ms`

### Q3：`no questions generated`

- LLM Key 无效 / 余额不足  
- RAG 检索不到内容（KB 为空或未索引）  
- 查看 `data\user\logs\deeptutor.jsonl` 与对应 session 的 chat 事件

### Q4：Question Bank 按 KB 筛选数量对不上

- 历史题可能 **未标注 kb_name**；重启后端会尝试 **自动回填**  
- 下拉框选「**未标注知识库**」可查看仍无标签的题  
- 详见 Fork README / Question Bank KB 筛选说明

### Q5：auto_export 的文件在哪？

```text
D:\Dev\DeepTutor\data\user\exports\{job_id}-{unix_timestamp}.xlsx
```

仅含 **该次定时运行** 生成的题目。

---

## 10. 推荐 nightly 检查清单

```text
□ deeptutor 窗口仍开着（或计划任务已启动服务）
□ 电源：睡眠已关闭或合盖不休眠
□ scheduled_quiz.yaml 中 kb_name 正确、enabled: true
□ GET /api/v1/scheduled-quiz/jobs 中 next_run_at 合理
□ LLM API 可用
□ 次日：scheduled_quiz_state.json last_status = ok
□ 次日：exports/ 有新 xlsx（若 auto_export: true）
□ Question Bank 按 KB 筛选有新题
```

---

## 11. 相关文档

- [Phase 1 计划](phase1-plan.md) — M6/M7 里程碑  
- [SECONDARY_DEV.md](../SECONDARY_DEV.md) — 开发启动与路径  
- [UPSTREAM.md](../UPSTREAM.md) — 同步官方 DeepTutor

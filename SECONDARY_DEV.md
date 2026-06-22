# DeepTutor Secondary Development

Custom fork for:

- Knowledge-base-scoped quiz deduplication
- Excel export of generated questions
- Scheduled overnight quiz generation
- (Phase 2) Parallel workers + embedding dedup

## Docs

- [Phase 1 plan](docs/phase1-plan.md)
- [Phase 2 plan](docs/phase2-plan.md)
- [Upstream sync](UPSTREAM.md)

## Paths (D 盘)

| 用途 | 路径 |
|------|------|
| 源码 / Fork 仓库 | `D:\Dev\deeptutorSecondaryDevlopment` |
| 运行工作区（数据、题库、KB） | `D:\Dev\DeepTutor` |

> 2026-06-22 起项目已从 C 盘迁至 D 盘，避免系统盘占满。旧路径 `C:\Users\36739\...` 可在关闭 Cursor 后手动删除。

## Quick start (dev)

> **Windows 说明**：本机 `pip` / `deeptutor` **不在 PATH**，请用下面带完整路径的命令，或运行 `scripts\` 下的脚本。
>
> **CMD 用户**：不要直接输入 `.\scripts\dev-start.ps1`（会用编辑器打开文件）。请用 **`scripts\dev-start.bat`**，或在 PowerShell 里运行 `.\scripts\dev-start.ps1`。

### 方式 A — 一键脚本（推荐）

**PowerShell：**

```powershell
cd D:\Dev\deeptutorSecondaryDevlopment
.\scripts\dev-install.ps1   # 首次初始化
.\scripts\dev-start.ps1       # 启动
```

**CMD（命令提示符）：**

```cmd
cd /d D:\Dev\deeptutorSecondaryDevlopment
scripts\dev-install.bat
scripts\dev-start.bat
```

### 方式 B — 手动命令

```powershell
# 1. 后端（editable 安装，只需一次）
cd D:\Dev\deeptutorSecondaryDevlopment
D:\python3.12\python.exe -m pip install -e .

# 2. 前端依赖（源码模式必须，只需一次）
cd D:\Dev\deeptutorSecondaryDevlopment\web
npm install

# 3. 启动（工作区在 D 盘）
cd D:\Dev\DeepTutor
D:\python3.12\Scripts\deeptutor.exe start
```

### 可选：把 Python 加入 PATH

将 `D:\python3.12` 和 `D:\python3.12\Scripts` 加入系统环境变量 PATH 后，可直接使用 `pip` 和 `deeptutor`。

或指定工作区根目录：

```powershell
D:\python3.12\Scripts\deeptutor.exe start --home D:\Dev\DeepTutor
```

## Branch strategy

- `main` — stable fork baseline synced from upstream + merged features
- `dev/phase1` — active Phase 1 work

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

```powershell
cd D:\Dev\deeptutorSecondaryDevlopment
pip install -e .
cd D:\Dev\DeepTutor
D:\python3.12\Scripts\deeptutor.exe init    # 首次在新工作区
D:\python3.12\Scripts\deeptutor.exe start
```

或指定工作区根目录：

```powershell
D:\python3.12\Scripts\deeptutor.exe start --home D:\Dev\DeepTutor
```

## Branch strategy

- `main` — stable fork baseline synced from upstream + merged features
- `dev/phase1` — active Phase 1 work

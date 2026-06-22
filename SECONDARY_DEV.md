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

## Quick start (dev)

```powershell
cd C:\Users\36739\deeptutorSecondaryDevlopment
pip install -e .
cd C:\Users\36739\deeptutorSecondaryDevlopment   # workspace for data/
deeptutor init
deeptutor start
```

Use `C:\Users\36739\DeepTutor` as runtime workspace if you want to keep existing KB data, or copy `data/user` from the old install.

## Branch strategy

- `main` — stable fork baseline synced from upstream + merged features
- `dev/phase1` — active Phase 1 work

# Upstream Sync Guide

This repository is a secondary-development fork of [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor).

## Remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `upstream` | https://github.com/HKUDS/DeepTutor.git | Official releases |
| `origin` | https://github.com/JamesJen627/deeptutorSecondaryDevlopment.git | Our fork |

## Sync a new upstream release

```bash
git fetch upstream --tags
git checkout dev/phase1
git merge upstream/main   # resolve conflicts in our patched files
pip install -e .
```

## Local development

```bash
cd C:\Users\36739\deeptutorSecondaryDevlopment
pip install -e ".[dev]"   # or per pyproject instructions
deeptutor init
deeptutor start
```

Frontend (if developing UI):

```bash
cd web
npm install
npm run dev
```

## License

Upstream: Apache-2.0. Our changes remain under the same license unless noted otherwise.

# Environment Management Tools

This folder is the **source of truth** for all Poetry-related files and environment management tool configurations.

## Poetry Rule

**All Poetry-related files must be kept in this folder (`environment/python/tools/`):**
- `poetry.lock` - Lock file for reproducible builds
- `pyproject.toml` - Poetry configuration (authoritative copy)

## Note on Root Files

Poetry **requires** `pyproject.toml` and `poetry.lock` to exist in the project root to function. However:
- Root files are **ignored in git** (see `.gitignore`)
- **Source of truth**: Files in this `tools/` folder are tracked in git
- **Root files**: Local copies needed for Poetry to work (not tracked in git)
- **Workflow**: When updating Poetry config, update files in `tools/` first, then copy to root

**After cloning the repo**: Copy `pyproject.toml` and `poetry.lock` from `environment/python/tools/` to the project root for Poetry to function.

## Contents

- `poetry.lock`: Poetry lock file (for reproducible builds)
- `pyproject.toml`: Poetry configuration (source of truth)
- Other environment management tool configurations

# Environment Management Tools

This folder is the **source of truth** for all Poetry-related files and environment management tool configurations.

## Poetry Rule

**All Poetry-related files must be kept in this folder (`environment/python/tools/`):**
- `poetry.lock` - Lock file for reproducible builds
- `pyproject.toml` - Poetry configuration (authoritative copy)

## Note on pyproject.toml

Poetry requires `pyproject.toml` to exist in the project root. The root version is a copy that Poetry needs to function. The authoritative version is kept here in `tools/`. When making changes to Poetry configuration, update the file in this folder first, then sync to root.

## Contents

- `poetry.lock`: Poetry lock file (for reproducible builds)
- `pyproject.toml`: Poetry configuration (source of truth)
- Other environment management tool configurations

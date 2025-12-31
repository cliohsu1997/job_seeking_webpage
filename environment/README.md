# Environment Folder

This folder contains all environment management tools and configurations.

## Structure

```
environment/
├── python/
│   ├── tools/                    # Environment management tools (Poetry configs, lock files)
│   │   ├── poetry.lock          # Poetry lock file (also symlinked to root)
│   │   └── README.md            # Tools folder documentation
│   └── venv/                    # Actual virtual environment (managed by Poetry)
└── README.md                    # This file
```

## Contents

### `python/tools/`
- **poetry.lock**: Poetry lock file for reproducible builds
- Other environment management tool configurations and lock files

### `python/venv/`
- Poetry virtual environment - automatically created and managed by Poetry
- Contains all installed Python packages

## Configuration

Poetry is configured to use this folder structure via:
```bash
poetry config virtualenvs.path ./environment/python/venv
```

## Notes

- The virtual environment (`venv/`) is automatically created when running `poetry install`
- Do not manually edit files in `venv/` - they are managed by Poetry
- `poetry.lock` is stored in `tools/` for organization but also needs to be in project root for Poetry to work
- The `venv/` folder is excluded from git (see `.gitignore`)
- `poetry.lock` should be committed for reproducible builds

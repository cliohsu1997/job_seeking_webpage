# Read It First

**Cursor Rule:** Before starting or continuing a conversation, read this file to stay aligned on context, priorities, and rules.

## Mandatory First Steps

1. Read `conversation_cursor/progress/latest.md` to identify main tasks (phases) in progress
2. Read corresponding to-do list in `conversation_cursor/to-do-list/` (format: `YYYY-MM-DD_phase-name.md`)
3. Read `conversation_cursor/structure/latest.md` for project structure
4. Check today's dated folder in `conversation_cursor/dates/YYYY-MM-DD/` for context
5. Confirm new requests align with recorded goals to avoid duplicate work
6. Mention this file when summarizing updates

**Workflow**: Progress shows main tasks → To-do lists show subtasks

## Environment Information

- **Python**: `C:\Users\clioh\AppData\Local\Programs\Python\Python313\python.exe` (3.13.5)
- **Poetry**: `C:\Users\clioh\AppData\Roaming\pypoetry\venv\Scripts\poetry.exe`
- **Virtual Environment**: `./environment/python/venv/`
- **Environment Tools**: `./environment/python/tools/` (all Poetry-related files: poetry.lock, pyproject.toml copy, configs)
- **Poetry Rule**: All Poetry-related files must be kept in `environment/python/tools/` (source of truth). Root `pyproject.toml` and `poetry.lock` are ignored in git - they exist locally for Poetry to function but are copies from tools/.

## Running Python

### Activate Virtual Environment
```bash
# Windows PowerShell
.\environment\python\venv\Scripts\Activate.ps1

# Windows CMD
.\environment\python\venv\Scripts\activate.bat
```

### Run Python
```bash
python script.py
python -m module_name
python tests/setup-project/test_python_setup.py
```

## Coding & Workflow Rules

### Code Formatting
- Break each argument on its own line
- Always explain code before implementing

### DRY Principle
- Avoid duplication; extract reusable functions/classes
- Reuse existing patterns; refactor similar code into shared modules
- Keep configuration centralized (e.g., `data/config/`)

### Workflow Structure
- Default flow: `load → transform → export`

### Phase & File Naming
- **Phase names**: Start with verb, be informative (e.g., `setup-project`, `load-data-collection`, `transform-data-processing`, `export-output-generation`)
- **To-do lists**: `YYYY-MM-DD_phase-name.md` (matches phase naming)
- **Proposals**: Name with verb (e.g., `create-cursor-rule.md`)

### Progress & To-Do Lists
- Each to-do list = one complete phase task
- Use checkboxes `- [ ]` and `- [x]`
- When all tasks complete, mark phase complete in progress file
- Progress = high-level stages; To-do = actionable subtasks

### Test Structure
- Tests in `tests/` with subfolders matching phase names (e.g., `tests/setup-project/`, `tests/load-data-collection/`)

### Git & File Management
- **Commits**: Each commit = one minimum complete task
- **.gitkeep files**: Only keep essential ones (e.g., empty folders that must exist). Do not regenerate unnecessarily. Remove when folders contain actual files.

### End of Conversation/Task
- Reorganize structure/progress/to-do files to show:
  - What's accomplished
  - What's next
  - Update progress with "What We've Accomplished" and "What's Next"
  - Ensure to-do list names match phase names
  - Clean up unnecessary files (including .gitkeep)

### Communication
- Keep workflow conversational
